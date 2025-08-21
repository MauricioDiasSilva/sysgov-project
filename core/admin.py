# SysGov_Project/core/admin.py

from django.contrib import admin
# Remova EstudoTecnicoPreliminar e TermoDeReferencia da importação
from .models import Processo

admin.site.register(Processo)
# Remova estas linhas:
# admin.site.register(EstudoTecnicoPreliminar)
# admin.site.register(TermoDeReferencia)