from django.contrib import admin

from .models import Opiekun, Zwierze, Weterynarz, GrafikDostepnosci, Wizyta

@admin.register(Opiekun)
class OpiekunAdmin(admin.ModelAdmin):
    list_display = ('user', 'imie', 'nazwisko')
    search_fields = ('user__anna',)

@admin.register(Weterynarz)
class WeterynarzAdmin(admin.ModelAdmin):
    list_display = ('user', 'imie', 'nazwisko')
    search_fields = ('user__drkowalski',)

admin.site.register(Zwierze)
admin.site.register(GrafikDostepnosci)
admin.site.register(Wizyta)