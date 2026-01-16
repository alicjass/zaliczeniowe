from django.db import models

PLEC = models.IntegerChoices(
    'Plec',
    'Kobieta Mezczyzna Inna'
)

TYP_OSOBA = models.IntegerChoices(
    'TypOsoba',
    'Admin Weterynarz Opiekun'
)

STATUS_OSOBA = models.IntegerChoices(
    'StatusOsoba',
    'Aktywny Nieaktywny'
)

STATUS_WIZYTA = models.IntegerChoices(
        'StatusWizyta',
        'Zaplanowana Otwarta Zrealizowana Odwolana Nieodwolana'
)

GATUNEK = models.IntegerChoices(
    'Gatunek',
    'Pies Kot'
)

class Osoba(models.Model):
    imie = models.CharField(max_length = 50, blank = False, null = False)
    nazwisko = models.CharField(max_length = 100, blank = False, null = False)
    plec = models.IntegerField(choices = PLEC.choices, default = PLEC.Inna)
    typ = models.IntegerField(choices = TYP_OSOBA.choices, blank = False, null = False)
    status = models.IntegerField(choices = STATUS_OSOBA.choices, default = STATUS_OSOBA.Aktywny)
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"Osoba: {self.imie} {self.nazwisko} ({self.get_typ_display()})"
    
    class Meta:
        ordering = ['typ', 'nazwisko', 'imie']


class Zwierze(models.Model):
    imie = models.CharField(max_length = 50, blank = False, null = False)
    opiekun = models.ForeignKey(Osoba, on_delete = models.CASCADE, limit_choices_to={'typ': TYP_OSOBA.Opiekun})
    gatunek = models.IntegerField(choices = GATUNEK.choices, blank = False, null = False)
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"Zwierze: {self.imie} ({self.get_gatunek_display()} {self.opiekun.nazwisko})"

    class Meta:
        ordering = ['gatunek', 'imie']