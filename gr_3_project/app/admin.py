from django.contrib import admin

from .models import Opiekun, Zwierze, Weterynarz, GrafikDostepnosci, Wizyta

admin.site.register(Opiekun)
admin.site.register(Zwierze)
admin.site.register(Weterynarz)
admin.site.register(GrafikDostepnosci)
admin.site.register(Wizyta)