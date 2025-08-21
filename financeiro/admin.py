# SysGov_Project/financeiro/admin.py

from django.contrib import admin
# Mude: from .models import DocumentoFiscal, NotaFiscal # Import your key models
# Para:
from .models import DocumentoFiscal, Pagamento # <<< Importa os modelos corretos

# ... (outros modelos de financeiro que você queira registrar) ...

# Registra seus modelos no painel de administração
admin.site.register(DocumentoFiscal)
admin.site.register(Pagamento) # <<< Registre Pagamento também se desejar