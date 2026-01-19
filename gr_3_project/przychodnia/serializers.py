from rest_framework import serializers
from .models import Opiekun, Zwierze, Weterynarz, GrafikDostepnosci, Wizyta

class OpiekunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opiekun
        fields = '__all__'

    def validate_imie(self, value):
        if not (value[0].isupper() and value.isalpha()):
            raise serializers.ValidationError(
                "Imię powinno zawierać tylko litery i rozpoczynać się wielką literą!"
                )
        return value

    def validate_nazwisko(self, value):
        if not (value[0].isupper() and value.isalpha()):
            raise serializers.ValidationError(
                "Nazwisko powinno zawierać tylko litery i rozpoczynać się wielką literą!"
                )
        return value


class ZwierzeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zwierze
        fields = '__all__'

    def validate_imie(self, value):
        if not (value[0].isupper() and value.isalpha()):
            raise serializers.ValidationError(
                "Imię powinno zawierać tylko litery i rozpoczynać się wielką literą!"
                )
        return value

    def validate_data_urodzenia(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("Data urodzenia nie może być z przyszłości.")
        return value


class WeterynarzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weterynarz
        fields = '__all__'

    def validate_imie(self, value):
        if not (value[0].isupper() and value.isalpha()):
            raise serializers.ValidationError(
                "Imię powinno zawierać tylko litery i rozpoczynać się wielką literą!"
                )
        return value

    def validate_nazwisko(self, value):
        if not (value[0].isupper() and value.isalpha()):
            raise serializers.ValidationError(
                "Nazwisko powinno zawierać tylko litery i rozpoczynać się wielką literą!"
                )
        return value


class GrafikDostepnosciSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrafikDostepnosci
        fields = '__all__'

    def validate(self, data):
        if data['data'] < date.today():
            raise serializers.ValidationError("Data nie może być z przeszłości.")
        
        if data['godz_od'] >= data['godz_do']:
            raise serializers.ValidationError("Godzina rozpoczęcia nie może być późniejsza niż godzina zakończenia.")
        return data


class WizytaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wizyta
        fields = '__all__'

    def validate_termin_wizyty(self, value):
        if value < datetime.now():
            raise serializers.ValidationError("Nie można umówić wizyty na datę z przeszłości.")
        return value