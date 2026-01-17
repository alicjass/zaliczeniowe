from django.contrib import admin

from .models import Opiekun, Zwierze, Weterynarz, DostepnoscWeterynarza, Wizyta

admin.site.register(Opiekun)
admin.site.register(Zwierze)
admin.site.register(Weterynarz)
admin.site.register(DostepnoscWeterynarza)
admin.site.register(Wizyta)