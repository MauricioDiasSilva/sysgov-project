# SysGov_Project/integracao_audesp/admin.py

from django.contrib import admin
from .models import (
    AudespConfiguracao,
    SubmissaoAudesp,
    AudespAjusteContratual,
    AudespAtaRegistroPrecos, # Importado
    AudespEmpenhoContrato # Importado
)

# Opcional: Para uma visualização mais detalhada no Admin
class SubmissaoAudespAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'tipo_documento', 'content_object', 'status',
        'data_submissao', 'enviado_por',
    )
    list_filter = ('status', 'tipo_documento', 'data_submissao')
    search_fields = ('mensagem_status', 'content_type__model', 'object_id')
    readonly_fields = ('data_submissao', 'enviado_por', 'content_type', 'object_id', 'content_object')
    date_hierarchy = 'data_submissao'

class AudespAjusteContratualAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_contrato_audesp', 'nome_razao_social_fornecedor', 'tipo_contrato_id',
        'data_assinatura', 'valor_global', 'retificacao', 'processo_vinculado'
    )
    list_filter = ('tipo_contrato_id', 'retificacao', 'data_assinatura', 'processo_vinculado')
    search_fields = (
        'codigo_contrato_audesp', 'numero_contrato_empenho', 'nome_razao_social_fornecedor',
        'ni_fornecedor', 'objeto_contrato'
    )
    raw_id_fields = ('processo_vinculado', 'resultado_licitacao_origem', 'edital_origem', 'criado_por')
    date_hierarchy = 'data_assinatura'

class AudespAtaRegistroPrecosAdmin(admin.ModelAdmin): # NOVO ADMIN PARA ATA RP
    list_display = (
        'codigo_ata_audesp', 'numero_ata_registro_preco', 'ano_ata', 'data_assinatura',
        'data_vigencia_fim', 'edital_origem', 'processo_vinculado'
    )
    list_filter = ('ano_ata', 'retificacao', 'data_assinatura', 'processo_vinculado')
    search_fields = ('codigo_ata_audesp', 'numero_ata_registro_preco', 'codigo_edital_audesp')
    raw_id_fields = ('processo_vinculado', 'edital_origem', 'criado_por')
    date_hierarchy = 'data_assinatura'

class AudespEmpenhoContratoAdmin(admin.ModelAdmin): # NOVO ADMIN PARA EMPENHO
    list_display = (
        'numero_empenho', 'ano_empenho', 'data_emissao_empenho',
        'codigo_contrato_audesp', 'retificacao', 'processo_vinculado'
    )
    list_filter = ('ano_empenho', 'retificacao', 'data_emissao_empenho')
    search_fields = ('numero_empenho', 'codigo_contrato_audesp')
    raw_id_fields = ('ajuste_contratual_audesp', 'documento_fiscal_origem', 'processo_vinculado', 'criado_por')
    date_hierarchy = 'data_emissao_empenho'


# Registra os modelos no painel de administração
admin.site.register(AudespConfiguracao)
admin.site.register(SubmissaoAudesp, SubmissaoAudespAdmin)
admin.site.register(AudespAjusteContratual, AudespAjusteContratualAdmin)
admin.site.register(AudespAtaRegistroPrecos, AudespAtaRegistroPrecosAdmin) # Registro da Ata RP
admin.site.register(AudespEmpenhoContrato, AudespEmpenhoContratoAdmin) # Registro do Empenho