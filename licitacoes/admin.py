# SysGov_Project/sysgov_project/licitacoes/admin.py

from django.contrib import admin
from .models import Edital, Lote, ItemLicitado, ResultadoLicitacao # <<< Importe o novo modelo

admin.site.register(Edital)
admin.site.register(Lote)
admin.site.register(ItemLicitado)
admin.site.register(ResultadoLicitacao) # <<< Registre o novo modelo