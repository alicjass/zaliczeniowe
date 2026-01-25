from django.db import models
from django.contrib.auth.models import User

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # polaczenie profilu opiekuna z kontem uzytkownika User

    imie = models.CharField(max_length = 50)
    nazwisko = models.CharField(max_length = 100)
    plec = models.IntegerField(choices = PLEC_OSOBA.choices)
    
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
    
    class Meta:
        verbose_name_plural = "Opiekunowie"
        ordering = ['nazwisko', 'imie']


class Zwierze(models.Model):
    imie = models.CharField(max_length = 50)
    opiekun = models.ForeignKey(Opiekun, on_delete = models.PROTECT)
    gatunek = models.IntegerField(choices = GATUNEK.choices)
    plec = models.IntegerField(choices = PLEC_ZWIERZE.choices)
    data_urodzenia = models.DateField(blank = True, null = True)

    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"{self.imie} ({self.get_gatunek_display()})"

    class Meta:
        verbose_name_plural = "Zwierzeta"
        ordering = ['opiekun__nazwisko', 'gatunek', 'imie']


class Weterynarz(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # polaczenie profilu weterynarza z kontem uzytkownika User

    imie = models.CharField(max_length = 50)
    nazwisko = models.CharField(max_length = 100)
    plec = models.IntegerField(choices = PLEC_OSOBA.choices)
    specjalizacja = models.CharField(max_length=100, blank=True)
    
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
    
    class Meta:
        verbose_name_plural = "Weterynarze"
        ordering = ['nazwisko', 'imie']


class Wizyta(models.Model):
    zwierze = models.ForeignKey(Zwierze, on_delete = models.CASCADE)
    weterynarz = models.ForeignKey(Weterynarz, on_delete = models.PROTECT)
    data_wizyty = models.DateField()  # warunek: weterynarz jest dostepny (nie ma kolizji z innymi wizytami)
    godzina_wizyty = models.TimeField()
    status = models.IntegerField(choices = STATUS_WIZYTA.choices, default = STATUS_WIZYTA.Zaplanowana)
    notatka = models.TextField(blank = True)

    def __str__(self):
        return f"{self.zwierze.imie}: {self.data_wizyty.strftime('%d.%m.%Y')} {self.godzina_wizyty.strftime('%H:%M')} (lek. wet. {self.weterynarz.nazwisko})"

    class Meta:
        verbose_name_plural = "Wizyty"
        ordering = ['data_wizyty', 'godzina_wizyty', 'status']