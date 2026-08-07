from django.contrib import admin
from .models import Setor, Equipamento, Manutencao, OficinaExterna

admin.site.register(Setor)
admin.site.register(Equipamento)
admin.site.register(Manutencao)
admin.site.register(OficinaExterna)