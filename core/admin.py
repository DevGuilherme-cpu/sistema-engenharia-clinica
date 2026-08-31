from django.contrib import admin
from .models import Setor, Equipamento, Manutencao, OficinaExterna, GuiaMovimentacao, TermoEntrega

admin.site.register(Setor)
admin.site.register(Equipamento)
admin.site.register(Manutencao)
admin.site.register(OficinaExterna)
admin.site.register(GuiaMovimentacao)
admin.site.register(TermoEntrega)