from django import forms
from django.core.exceptions import ValidationError
from datetime import date, datetime
from .models import Wizyta, Zwierze, Weterynarz


class WizytaForm(forms.ModelForm):
    class Meta:
        model = Wizyta
        fields = ["zwierze", "weterynarz", "data_wizyty", "godzina_wizyty"]
        widgets = {
            'data_wizyty': forms.DateInput(attrs={'type': 'date'}),
            'godzina_wizyty': forms.Select(choices=[(f"{h:02d}:{m:02d}", f"{h:02d}:{m:02d}") for h in range(24) for m in (0, 30)]),
        }

    def __init__(self, *args, **kwargs):
        self.opiekun = kwargs.pop("opiekun")
        super().__init__(*args, **kwargs)

        self.fields["zwierze"].queryset = Zwierze.objects.filter(opiekun=self.opiekun)

    def clean(self):
        super().clean()
        if self.cleaned_data.get('data_wizyty') and self.cleaned_data.get('godzina_wizyty'):
            if datetime.combine(self.cleaned_data['data_wizyty'], self.cleaned_data['godzina_wizyty']) < datetime.now():
                raise ValidationError("Nie można umówić wizyty w przeszłości!")
        return self.cleaned_data