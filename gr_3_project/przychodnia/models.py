from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

PLEC_OSOBA = models.IntegerChoices(
    'PlecOsoba',
    'Mężczyzna Kobieta Inna'
)

GATUNEK = models.IntegerChoices(
    'Gatunek',
    'Pies Kot'
)

PLEC_ZWIERZE = models.IntegerChoices(
    'PlecZwierze',
    'Samiec Samica'
)

STATUS_WIZYTA = models.IntegerChoices(
    'StatusWizyta',
    'Zaplanowana Zrealizowana Odwołana'
)


class Opiekun(models.Model):
    """Model opiekuna zwierzaka"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # polaczenie profilu opiekuna z kontem uzytkownika User

    imie = models.CharField(max_length = 50)
    nazwisko = models.CharField(max_length = 100)
    plec = models.IntegerField(choices = PLEC_OSOBA.choices, default = PLEC_OSOBA.Inna)
    
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
    
    class Meta:
        verbose_name_plural = "Opiekunowie"
        ordering = ['nazwisko', 'imie']


class Zwierze(models.Model):
    """Model zwierzaka, którego opiekun umawia na wizyty"""
    imie = models.CharField(max_length = 50)
    opiekun = models.ForeignKey(Opiekun, on_delete = models.CASCADE)
    gatunek = models.IntegerField(choices = GATUNEK.choices)
    plec = models.IntegerField(choices = PLEC_ZWIERZE.choices)
    data_urodzenia = models.DateField(blank = True, null = True)  # opcjonalnie

    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"{self.imie} ({self.get_gatunek_display()})"

    class Meta:
        verbose_name_plural = "Zwierzeta"
        ordering = ['opiekun__nazwisko', 'gatunek', 'imie']


class Weterynarz(models.Model):
    """Model weterynarza, który przeprowadza wizyty"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # polaczenie profilu weterynarza z kontem uzytkownika User

    imie = models.CharField(max_length = 50)
    nazwisko = models.CharField(max_length = 100)
    plec = models.IntegerField(choices = PLEC_OSOBA.choices, default = PLEC_OSOBA.Inna)
    specjalizacja = models.CharField(max_length=100, blank=True)  # opcjonalnie
    
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
    
    class Meta:
        verbose_name_plural = "Weterynarze"
        ordering = ['nazwisko', 'imie']


class Wizyta(models.Model):
    """Model wizyty weterynaryjnej"""
    zwierze = models.ForeignKey(Zwierze, on_delete = models.SET_NULL, null=True)
    weterynarz = models.ForeignKey(Weterynarz, on_delete = models.PROTECT)
    data_wizyty = models.DateField()
    godzina_wizyty = models.TimeField()
    status = models.IntegerField(choices = STATUS_WIZYTA.choices, default = STATUS_WIZYTA.Zaplanowana)
    notatka = models.TextField(blank = True)  # obowiązkowa dopiero po zrealizowaniu wizyty

    @classmethod  # metoda działająca na klasie, nie na obiekcie
    def aktualizuj_przeterminowane_wizyty(cls):
        """Zmienia status na "Odwołana" dla wizyt zaplanowanych, które minęły ponad 1h temu."""
        
        for wizyta in cls.objects.filter(status=STATUS_WIZYTA.Zaplanowana):
            czas_wizyty = datetime.combine(wizyta.data_wizyty, wizyta.godzina_wizyty)
            if czas_wizyty + timedelta(hours=1) < datetime.now():
                wizyta.status = STATUS_WIZYTA.Odwołana
                wizyta.save()

    def __str__(self):
        zwierze_nazwa = self.zwierze.imie if self.zwierze else "[Usunięte zwierzę]"
        return f"{zwierze_nazwa}: {self.data_wizyty.strftime('%d.%m.%Y')} {self.godzina_wizyty.strftime('%H:%M')} (weterynarz: {self.weterynarz.nazwisko})"

    class Meta:
        verbose_name_plural = "Wizyty"
        ordering = ['data_wizyty', 'godzina_wizyty', 'status']