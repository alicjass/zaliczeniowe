from django.db import models

PLEC_OSOBA = models.IntegerChoices(
    'PlecOsoba',
    'Mezczyzna Kobieta Inna'
)

TYP_OSOBA = models.IntegerChoices(
    'TypOsoba',
    'Admin Weterynarz Opiekun'
)

STATUS_AKTYWNOSC = models.IntegerChoices(
    'StatusAktywnosc',
    'Aktywny Nieaktywny'
)

PLEC_ZWIERZE = models.IntegerChoices(
    'PlecZwierze',
    'Samiec Samica'
)

GATUNEK = models.IntegerChoices(
    'Gatunek',
    'Pies Kot'
)

STATUS_WIZYTA = models.IntegerChoices(
    'StatusWizyta',
    'Zaplanowana Otwarta Zrealizowana Odwolana Nieodwolana'
)


class Osoba(models.Model):
    imie = models.CharField(max_length = 50)
    nazwisko = models.CharField(max_length = 100)
    plec = models.IntegerField(choices = PLEC_OSOBA.choices, default = PLEC_OSOBA.Inna)
    typ = models.IntegerField(choices = TYP_OSOBA.choices)
    status = models.IntegerField(choices = STATUS_AKTYWNOSC.choices, default = STATUS_AKTYWNOSC.Aktywny)
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"Osoba: {self.imie} {self.nazwisko}, ({self.get_typ_display()})"
    
    class Meta:
        ordering = ['nazwisko', 'imie']


class Zwierze(models.Model):
    imie = models.CharField(max_length = 50)
    opiekun = models.ForeignKey(Osoba, on_delete = models.PROTECT, limit_choices_to={'typ': TYP_OSOBA.Opiekun})
    gatunek = models.IntegerField(choices = GATUNEK.choices)
    plec = models.IntegerField(choices = PLEC_ZWIERZE.choices)
    data_urodzenia = models.DateField(blank = True, null = True)  # warunek: nie moze byc z przyszlosci!
    status = models.IntegerField(choices = STATUS_AKTYWNOSC.choices, default = STATUS_AKTYWNOSC.Aktywny)
    data_dodania = models.DateTimeField(auto_now_add = True, editable = False)

    def __str__(self):
        return f"Zwierzę: {self.imie} ({self.opiekun.nazwisko}, {self.get_gatunek_display()})"

    class Meta:
        ordering = ['gatunek', 'imie']


class Wizyta(models.Model):
    zwierze = models.ForeignKey(Zwierze, on_delete = models.PROTECT)
    weterynarz = models.ForeignKey(Osoba, on_delete = models.PROTECT, limit_choices_to={'typ': TYP_OSOBA.Weterynarz})
    data_wizyty = models.DateTimeField()  # warunek: nie mozna umowic wizyty na date z przeszlosci + nie mozna zmienic wizyty odbytej
    status = models.IntegerField(choices = STATUS_WIZYTA.choices, default = STATUS_WIZYTA.Zaplanowana)
    notatka = models.TextField(blank = True, null = True)

    def __str__(self):
        return f"Wizyta: {self.zwierze.imie} ({self.data_wizyty}, lek. wet. {self.weterynarz.nazwisko})"

    class Meta:
        ordering = ['data_wizyty']


class DostepnoscWeterynarza(models.Model):
    weterynarz = models.ForeignKey(Osoba, on_delete = models.PROTECT, limit_choices_to={'typ': TYP_OSOBA.Weterynarz})
    data = models.DateField()
    godz_od = models.TimeField() # warunek: godz_od < godz_do
    godz_do = models.TimeField()

    def __str__(self):
        return f"Dostępność lek. wet. {self.weterynarz.nazwisko}: {self.data} {self.godz_od} - {self.godz_do}"

    class Meta:
        ordering = ['data']