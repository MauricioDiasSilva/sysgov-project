# SysGov_Project/integracao_audesp/forms.py

from django import forms
# Importe todos os modelos AUDESP do próprio app, incluindo os CHOICES
from .models import (
    AudespAjusteContratual, AudespAtaRegistroPrecos, AudespEmpenhoContrato,
    AudespConfiguracao, SubmissaoAudesp, AudespEditalDetalhado,
    AUDESP_TIPO_CONTRATO_CHOICES, AUDESP_CATEGORIA_PROCESSO_CHOICES,
    AUDESP_TIPO_PESSOA_CHOICES, AUDESP_TIPO_OBJETO_CONTRATO_CHOICES,
    AUDESP_RECURSO_BID_CHOICES, AUDESP_OBJECION_BID_CHOICES, AUDESP_TIPO_NATUREZA_CHOICES,
    AUDESP_INTERPOSICAO_RECURSO_CHOICES, AUDESP_EXIGENCIA_GARANTIA_CHOICES,
    AUDESP_EXIGENCIA_AMOSTRA_CHOICES, AUDESP_EXIGENCIA_INDICES_ECONOMICOS_CHOICES,
    AUDESP_TIPO_INDICE_CHOICES, AUDESP_TIPO_ORCAMENTO_CHOICES, AUDESP_SITUACAO_COMPRA_ITEM_CHOICES,
    AUDESP_TIPO_VALOR_PROPOSTA_CHOICES, AUDESP_TIPO_PROPOSTA_CHOICES,
    AUDESP_DECLARACAO_ME_EPP_CHOICES, AUDESP_RESULTADO_HABILITACAO_CHOICES,
)
# Importar modelos de outros apps para ForeignKeys no formulário
from core.models import Processo
from licitacoes.models import Edital, ResultadoLicitacao
from financeiro.models import DocumentoFiscal


class AudespAjusteContratualForm(forms.ModelForm):
    class Meta:
        model = AudespAjusteContratual
        fields = [
            'processo_vinculado', 'resultado_licitacao_origem', 'edital_origem',
            'adesao_participacao', 'gerenciadora_jurisdicionada', 'cnpj_gerenciadora',
            'municipio_gerenciador', 'entidade_gerenciadora', 'codigo_edital_audesp',
            'codigo_ata_rp_audesp', 'codigo_contrato_audesp', 'retificacao',
            'fonte_recursos_contratacao', 'itens_contratados_ids', 'tipo_contrato_id',
            'numero_contrato_empenho', 'ano_contrato', 'processo_sistema_origem',
            'categoria_processo_id', 'receita', 'despesas_classificacao', 'codigo_unidade',
            'ni_fornecedor', 'tipo_pessoa_fornecedor', 'nome_razao_social_fornecedor',
            'ni_fornecedor_subcontratado', 'tipo_pessoa_fornecedor_subcontratado',
            'nome_razao_social_fornecedor_subcontratado', 'objeto_contrato',
            'informacao_complementar', 'valor_inicial', 'numero_parcelas', 'valor_parcela',
            'valor_global', 'valor_acumulado', 'data_assinatura', 'data_vigencia_inicio',
            'data_vigencia_fim', 'vigencia_meses', 'tipo_objeto_contrato',
        ]
        widgets = {
            'processo_vinculado': forms.Select(attrs={'class': 'form-select'}),
            'resultado_licitacao_origem': forms.Select(attrs={'class': 'form-select'}),
            'edital_origem': forms.Select(attrs={'class': 'form-select'}),
            'adesao_participacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gerenciadora_jurisdicionada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cnpj_gerenciadora': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio_gerenciador': forms.NumberInput(attrs={'class': 'form-control'}),
            'entidade_gerenciadora': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo_edital_audesp': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_ata_rp_audesp': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_contrato_audesp': forms.TextInput(attrs={'class': 'form-control'}),
            'retificacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fonte_recursos_contratacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ex: [1, 91]'}),
            'itens_contratados_ids': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ex: [1, 2, 3]'}),
            'tipo_contrato_id': forms.Select(attrs={'class': 'form-select'}),
            'numero_contrato_empenho': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_contrato': forms.NumberInput(attrs={'class': 'form-control'}),
            'processo_sistema_origem': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria_processo_id': forms.Select(attrs={'class': 'form-select'}),
            'receita': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'despesas_classificacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ex: ["12345678", "87654321"]'}),
            'codigo_unidade': forms.TextInput(attrs={'class': 'form-control'}),
            'ni_fornecedor': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_pessoa_fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'nome_razao_social_fornecedor': forms.TextInput(attrs={'class': 'form-control'}),
            'ni_fornecedor_subcontratado': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_pessoa_fornecedor_subcontratado': forms.Select(attrs={'class': 'form-select'}),
            'nome_razao_social_fornecedor_subcontratado': forms.TextInput(attrs={'class': 'form-control'}),
            'objeto_contrato': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'informacao_complementar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor_inicial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'numero_parcelas': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_parcela': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'valor_global': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'valor_acumulado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'data_assinatura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vigencia_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vigencia_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vigencia_meses': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_objeto_contrato': forms.Select(attrs={'class': 'form-select'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['processo_vinculado'].queryset = Processo.objects.all().order_by('numero_protocolo')
            self.fields['edital_origem'].queryset = Edital.objects.all().order_by('-data_publicacao')
            self.fields['resultado_licitacao_origem'].queryset = ResultadoLicitacao.objects.all().order_by('-data_homologacao')

            if self.instance.pk is None:
                if hasattr(self, 'request') and self.request.user.is_authenticated:
                    self.fields['criado_por'].initial = self.request.user.pk
            self.fields['criado_por'].widget.attrs['disabled'] = 'disabled'
            self.fields['criado_por'].widget.attrs['class'] = 'form-control-plaintext'


class AudespAtaRegistroPrecosForm(forms.ModelForm):
    class Meta:
        model = AudespAtaRegistroPrecos
        fields = [
            'processo_vinculado', 'edital_origem',
            'municipio', 'entidade', 'codigo_edital_audesp', 'codigo_ata_audesp',
            'ano_compra', 'retificacao', 'itens_licitados_ids',
            'numero_ata_registro_preco', 'ano_ata', 'data_assinatura',
            'data_vigencia_inicio', 'data_vigencia_fim',
        ]
        widgets = {
            'processo_vinculado': forms.Select(attrs={'class': 'form-select'}),
            'edital_origem': forms.Select(attrs={'class': 'form-select'}),
            'municipio': forms.NumberInput(attrs={'class': 'form-control'}),
            'entidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo_edital_audesp': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_ata_audesp': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'retificacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'itens_licitados_ids': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: [1, 5, 8]'}),
            'numero_ata_registro_preco': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_ata': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_assinatura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vigencia_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vigencia_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'processo_vinculado': 'Processo Principal',
            'edital_origem': 'Edital de Origem',
            'municipio': 'Município (Cód. AUDESP)',
            'entidade': 'Entidade (Cód. AUDESP)',
            'codigo_edital_audesp': 'Código Edital (AUDESP)',
            'codigo_ata_audesp': 'Código Ata (AUDESP)',
            'ano_compra': 'Ano da Compra',
            'retificacao': 'É Retificação?',
            'itens_licitados_ids': 'IDs dos Itens Licitados',
            'numero_ata_registro_preco': 'Número da Ata de Registro de Preço',
            'ano_ata': 'Ano da Ata',
            'data_assinatura': 'Data de Assinatura',
            'data_vigencia_inicio': 'Início da Vigência',
            'data_vigencia_fim': 'Fim da Vigência',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['processo_vinculado'].queryset = Processo.objects.all().order_by('numero_protocolo')
        self.fields['edital_origem'].queryset = Edital.objects.all().order_by('-data_publicacao')

        if self.instance.pk is None:
            if hasattr(self, 'request') and self.request.user.is_authenticated:
                self.fields['criado_por'].initial = self.request.user.pk
        self.fields['criado_por'].widget.attrs['disabled'] = 'disabled'
        self.fields['criado_por'].widget.attrs['class'] = 'form-control-plaintext'


class AudespEmpenhoContratoForm(forms.ModelForm):
    class Meta:
        model = AudespEmpenhoContrato
        fields = [
            'processo_vinculado', 'ajuste_contratual_audesp', 'documento_fiscal_origem',
            'municipio', 'entidade', 'codigo_contrato_audesp', 'retificacao',
            'numero_empenho', 'ano_empenho', 'data_emissao_empenho',
        ]
        widgets = {
            'processo_vinculado': forms.Select(attrs={'class': 'form-select'}),
            'ajuste_contratual_audesp': forms.Select(attrs={'class': 'form-select'}),
            'documento_fiscal_origem': forms.Select(attrs={'class': 'form-select'}),
            'municipio': forms.NumberInput(attrs={'class': 'form-control'}),
            'entidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo_contrato_audesp': forms.TextInput(attrs={'class': 'form-control'}),
            'retificacao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numero_empenho': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_empenho': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_emissao_empenho': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'processo_vinculado': 'Processo Principal',
            'ajuste_contratual_audesp': 'Ajuste Contratual de Origem',
            'documento_fiscal_origem': 'Documento Fiscal de Origem',
            'municipio': 'Município (Cód. AUDESP)',
            'entidade': 'Entidade (Cód. AUDESP)',
            'codigo_contrato_audesp': 'Código Contrato (AUDESP)',
            'retificacao': 'É Retificação?',
            'numero_empenho': 'Número do Empenho',
            'ano_empenho': 'Ano do Empenho',
            'data_emissao_empenho': 'Data de Emissão do Empenho',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['processo_vinculado'].queryset = Processo.objects.all().order_by('numero_protocolo')
        self.fields['ajuste_contratual_audesp'].queryset = AudespAjusteContratual.objects.all().order_by('-data_assinatura')
        self.fields['documento_fiscal_origem'].queryset = DocumentoFiscal.objects.all().order_by('-documento_fiscal_data_emissao')

        if self.instance.pk is None:
            if hasattr(self, 'request') and self.request.user.is_authenticated:
                self.fields['criado_por'].initial = self.request.user.pk
        self.fields['criado_por'].widget.attrs['disabled'] = 'disabled'
        self.fields['criado_por'].widget.attrs['class'] = 'form-control-plaintext'