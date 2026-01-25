from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from datetime import date, datetime
from .models import Zwierze, Weterynarz, Wizyta


class WizytaForm(forms.ModelForm):
    class Meta:
        model = Wizyta
        fields = ["zwierze", "weterynarz", "data_wizyty", "godzina_wizyty"]
        labels = {
            "zwierze": "Pacjent",
        }
        widgets = {
            'data_wizyty': forms.DateInput(attrs={'type': 'date'}),
            'godzina_wizyty': forms.Select(choices=[('', '--:--')] + [(f"{h:02d}:{m:02d}", f"{h:02d}:{m:02d}") for h in range(8, 18) for m in (0, 30)] + [('18:00', '18:00')]),
        }

    def __init__(self, *args, **kwargs):
        self.opiekun = kwargs.pop("opiekun")

        # przy przekładaniu wizyty ustawiamy aktualną jej godzinę jako wartość domyślną
        initial = kwargs.get('initial', {})
        if kwargs.get('instance') and kwargs['instance'].pk:
            initial['godzina_wizyty'] = kwargs['instance'].godzina_wizyty.strftime("%H:%M")
            kwargs['initial'] = initial
        
        super().__init__(*args, **kwargs)

        # do wyboru tylko zwierzęta danego opiekuna
        self.fields["zwierze"].queryset = Zwierze.objects.filter(opiekun=self.opiekun)

    def clean(self):
        super().clean()
        data_wizyty = self.cleaned_data.get('data_wizyty')
        godzina_wizyty = self.cleaned_data.get('godzina_wizyty')
        weterynarz = self.cleaned_data.get('weterynarz')
        
        if data_wizyty and godzina_wizyty:
            if datetime.combine(data_wizyty, godzina_wizyty) < datetime.now():
                raise ValidationError("Nie można umówić wizyty w przeszłości!")
            
            # sprawdzamy, czy weterynarz nie ma innej wizyty w tym terminie
            if weterynarz:
                istniejaca_wizyta = Wizyta.objects.filter(
                    weterynarz=weterynarz,
                    data_wizyty=data_wizyty,
                    godzina_wizyty=godzina_wizyty
                )
                
                # pomijamy aktualną wizytę
                if self.instance.pk:
                    istniejaca_wizyta = istniejaca_wizyta.exclude(pk=self.instance.pk)
                
                if istniejaca_wizyta.exists():
                    raise ValidationError(f"Lek. wet. {weterynarz} ma już wizytę o tej godzinie. Wybierz inny termin.")
        
        return self.cleaned_data


class NotatkaForm(forms.Form):
    notatka = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label=mark_safe("<strong style='display: block;'>Notatka medyczna:</strong>"),
        required=True,
        error_messages={'required': 'Proszę wprowadzić notatkę medyczną.'}
    )


class ZwierzeForm(forms.ModelForm):
    class Meta:
        model = Zwierze
        fields = ["imie", "gatunek", "plec", "data_urodzenia"]
        widgets = {
            'data_urodzenia': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            "imie": "Imię",
            "plec": "Płeć",
        }

    def __init__(self, *args, **kwargs):
        self.opiekun = kwargs.pop("opiekun")
        super().__init__(*args, **kwargs)

    # automatycznie zapisuje usera jako opiekuna stworzonego zwierzaka
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.opiekun = self.opiekun
        if commit:
            instance.save()
        return instance

    def clean_imie(self):
        value = self.cleaned_data.get('imie')
        if value and not (value[0].isupper() and value.isalpha()):
            raise ValidationError("Imię powinno zawierać tylko litery i rozpoczynać się wielką literą!")
        return value

    def clean_data_urodzenia(self):
        value = self.cleaned_data.get('data_urodzenia')
        if value and value > date.today():
            raise ValidationError("Data urodzenia nie może być z przyszłości!")
        return value