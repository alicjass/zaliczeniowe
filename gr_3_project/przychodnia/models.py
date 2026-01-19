from django.db import models
from django.contrib.auth.models import User

PLEC_OSOBA = models.IntegerChoices(
    'PlecOsoba',
    'Mezczyzna Kobieta Inna'
)

STATUS_AKTYWNOSC = models.IntegerChoices(
    'StatusAktywnosc',
    'Aktywny Nieaktywny'
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
    'Zaplanowana Otwarta Zrealizowana Odwolana Nieodwolana'
)


class Opiekun(models.Model):
    imie = models.CharField(max_length = 50)
    nazwisko = models.CharField(max_length = 100)
    plec = models.IntegerField(choices = PLEC_OSOBA.choices)
    
    status = models.IntegerField(choices = STATUS_AKTYWNOSC.choices, default = STATUS_AKTYWNOSC.Aktywny)
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

    status = models.IntegerField(choices = STATUS_AKTYWNOSC.choices, default = STATUS_AKTYWNOSC.Aktywny)
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"{self.imie} {self.opiekun.nazwisko} ({self.get_gatunek_display()})"

    class Meta:
        verbose_name_plural = "Zwierzeta"
        ordering = ['opiekun__nazwisko', 'gatunek', 'imie']


class Weterynarz(models.Model):
    imie = models.CharField(max_length = 50)
    nazwisko = models.CharField(max_length = 100)
    plec = models.IntegerField(choices = PLEC_OSOBA.choices)
    specjalizacja = models.CharField(max_length=100, blank=True)
    
    status = models.IntegerField(choices = STATUS_AKTYWNOSC.choices, default = STATUS_AKTYWNOSC.Aktywny)
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"
    
    class Meta:
        verbose_name_plural = "Weterynarze"
        ordering = ['nazwisko', 'imie']


class GrafikDostepnosci(models.Model):
    weterynarz = models.ForeignKey(Weterynarz, on_delete = models.CASCADE)
    data = models.DateField()
    godz_od = models.TimeField()
    godz_do = models.TimeField()

    def __str__(self):
        return f"lek. wet. {self.weterynarz.nazwisko}: {self.data} {self.godz_od.strftime('%H:%M')}-{self.godz_do.strftime('%H:%M')}"

    class Meta:
        verbose_name_plural = "Grafiki dostepnosci"
        ordering = ['data', 'godz_od']


class Wizyta(models.Model):
    zwierze = models.ForeignKey(Zwierze, on_delete = models.CASCADE)
    weterynarz = models.ForeignKey(Weterynarz, on_delete = models.PROTECT)
    termin_wizyty = models.DateTimeField()  # warunek: weterynarz jest dostepny (grafik dostepnosci + inne wizyty)
    status = models.IntegerField(choices = STATUS_WIZYTA.choices, default = STATUS_WIZYTA.Zaplanowana)
    notatka = models.TextField(blank = True)

    def __str__(self):
        return f"{self.zwierze.imie} {self.zwierze.opiekun.nazwisko}: {self.termin_wizyty.strftime('%Y-%m-%d %H:%M')} (lek. wet. {self.weterynarz.nazwisko})"

    class Meta:
        verbose_name_plural = "Wizyty"
        ordering = ['termin_wizyty']