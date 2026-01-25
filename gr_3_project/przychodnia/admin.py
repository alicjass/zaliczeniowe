from django.contrib import admin

from .models import Opiekun, Zwierze, Weterynarz, Wizyta

@admin.register(Opiekun)
class OpiekunAdmin(admin.ModelAdmin):
    list_display = ('user', 'imie', 'nazwisko')
    search_fields = ('user__username',)

@admin.register(Weterynarz)
class WeterynarzAdmin(admin.ModelAdmin):
    list_display = ('user', 'imie', 'nazwisko')
    search_fields = ('user__username',)

admin.site.register(Zwierze)
admin.site.register(Wizyta)