# SysGov_Project/financeiro/admin.py

from django.contrib import admin
from .models import DocumentoFiscal, Pagamento, NotaEmpenho

@admin.register(DocumentoFiscal)
class DocumentoFiscalAdmin(admin.ModelAdmin):
    # CORRIGIDO: Usando os nomes exatos do seu financeiro/models.py
    list_display = (
        'documento_fiscal_numero', 
        'documento_fiscal_valor', 
        'documento_fiscal_data_emissao', 
        'processo_vinculado'
    )
    list_filter = ('documento_fiscal_data_emissao',)
    search_fields = ('documento_fiscal_numero', 'processo_vinculado__titulo')
    raw_id_fields = ('processo_vinculado',)
    date_hierarchy = 'documento_fiscal_data_emissao'

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    # CORRIGIDO: Usando os nomes exatos do seu financeiro/models.py
    list_display = (
        'documento_fiscal_numero', 
        'nota_fiscal_valor_pago', 
        'nota_fiscal_pagto_dt', 
        'processo_vinculado'
    )
    list_filter = ('nota_fiscal_pagto_dt',)
    search_fields = ('documento_fiscal_numero', 'processo_vinculado__titulo')
    raw_id_fields = ('processo_vinculado',)
    date_hierarchy = 'nota_fiscal_pagto_dt'

@admin.register(NotaEmpenho)
class NotaEmpenhoAdmin(admin.ModelAdmin):
    # Este já estava correto, pois o modelo foi criado com base na nossa lógica
    list_display = ('numero_empenho', 'ano_empenho', 'fornecedor', 'valor', 'data_emissao', 'status')
    list_filter = ('status', 'ano_empenho', 'fornecedor')
    search_fields = ('numero_empenho', 'descricao', 'fornecedor__razao_social')
    raw_id_fields = ('contrato', 'fornecedor')
    date_hierarchy = 'data_emissao'