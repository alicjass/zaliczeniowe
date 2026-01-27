from django.contrib import admin
from .models import Opiekun, Zwierze, Weterynarz, Wizyta

@admin.register(Opiekun)
class OpiekunAdmin(admin.ModelAdmin):
    list_display = ('user', 'imie', 'nazwisko', 'plec', 'data_dodania')
    search_fields = ('imie', 'nazwisko', 'user__username')
    list_filter = ('plec', 'data_dodania')
    readonly_fields = ('data_dodania',)  # pole tylko do odczytu

@admin.register(Weterynarz)
class WeterynarzAdmin(admin.ModelAdmin):
    list_display = ('user', 'imie', 'nazwisko', 'plec', 'specjalizacja', 'data_dodania')
    search_fields = ('imie', 'nazwisko', 'user__username')
    list_filter = ('plec', 'specjalizacja', 'data_dodania')
    readonly_fields = ('data_dodania',)

@admin.register(Zwierze)
class ZwierzeAdmin(admin.ModelAdmin):
    list_display = ('imie', 'gatunek', 'plec', 'opiekun', 'data_urodzenia', 'data_dodania')
    search_fields = ('imie', 'opiekun__nazwisko')
    list_filter = ('gatunek', 'plec', 'opiekun', 'data_dodania')
    readonly_fields = ('data_dodania',)

@admin.register(Wizyta)
class WizytaAdmin(admin.ModelAdmin):
    list_display = ('zwierze', 'data_wizyty', 'godzina_wizyty', 'weterynarz', 'status')
    search_fields = ('zwierze__imie', 'weterynarz__nazwisko')
    list_filter = ('status', 'data_wizyty', 'weterynarz', 'zwierze__opiekun')
    date_hierarchy = 'data_wizyty'  # nawigacja po datach w panelu u góry