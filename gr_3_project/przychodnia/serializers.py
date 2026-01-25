from rest_framework import serializers
from .models import Opiekun, Zwierze, Weterynarz, Wizyta

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


class WizytaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wizyta
        fields = '__all__'

    def validate_termin_wizyty(self, value):
        if value < datetime.now():
            raise serializers.ValidationError("Nie można umówić wizyty na datę z przeszłości.")
        return value