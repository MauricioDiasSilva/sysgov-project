# contratacoes/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import (
    ETP, TR, PCA, ItemPCA, PesquisaPreco, ParecerTecnico,
    ItemCatalogo, RequisitoPadrao # Modelos que você já tinha
)
from ckeditor.widgets import CKEditorWidget

class ItemCatalogoForm(forms.ModelForm):
    class Meta:
        model = ItemCatalogo
        fields = ['nome_padronizado', 'descricao_tecnica', 'unidade_medida', 'preco_historico_medio']
        widgets = {
            'nome_padronizado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome padronizado do bem ou serviço'}),
            'descricao_tecnica': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Especificações técnicas detalhadas...'}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: UN, KG, SERVICO'}),
            'preco_historico_medio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'nome_padronizado': 'Nome Padronizado',
            'descricao_tecnica': 'Descrição Técnica',
            'unidade_medida': 'Unidade de Medida',
            'preco_historico_medio': 'Preço Histórico Médio (R$)',
        }

        
# 1. Formulário para Parecer Técnico
class ParecerTecnicoForm(forms.ModelForm):
    class Meta:
        model = ParecerTecnico
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput, forms.EmailInput, forms.URLInput)):
                field.widget.attrs.update({'class': 'form-control'})


class PesquisaPrecoForm(forms.ModelForm):
    class Meta:
        model = PesquisaPreco
        fields = '__all__' 
        widgets = {
            'data_pesquisa': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'data_pesquisa': 'Data da Pesquisa',
        }


# 3. Formulário para ETP (principal)
class ETPForm(forms.ModelForm):
    class Meta:
        model = ETP
        fields = [
            'titulo',
            'numero_processo',
            'setor_demandante',
            'item_pca_vinculado',
            'descricao_necessidade',
            'objetivo_contratacao',
            'requisitos_contratacao',
            'levantamento_solucoes_mercado',
            'estimativa_quantidades',
            'estimativa_valor',
            'resultados_esperados',
            'viabilidade_justificativa_solucao',
            'contratacoes_correlatas',
            'alinhamento_planejamento',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_processo': forms.TextInput(attrs={'class': 'form-control'}),
            'setor_demandante': forms.TextInput(attrs={'class': 'form-control'}),
            'item_pca_vinculado': forms.Select(attrs={'class': 'form-control'}),
            'descricao_necessidade': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'objetivo_contratacao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'requisitos_contratacao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'levantamento_solucoes_mercado': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'estimativa_quantidades': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'estimativa_valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'resultados_esperados': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'viabilidade_justificativa_solucao': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
            'contratacoes_correlatas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'alinhamento_planejamento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'estimativa_valor': 'Estimativa do Valor (R$)',
            'item_pca_vinculado': 'Vincular ao Item do PCA',
        }
        help_texts = {
            'estimativa_valor': 'Valor total estimado da contratação, em Reais.',
            'item_pca_vinculado': 'Selecione o item correspondente no PCA. Se não existir, o ETP poderá ser reprovado.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput, forms.EmailInput, forms.URLInput)):
                field.widget.attrs.update({'class': 'form-control'})


# 4. Formset para Pesquisas de Preço (usa PesquisaPrecoForm e ETP)
PesquisaPrecoFormSet = inlineformset_factory(
    ETP,
    PesquisaPreco,
    form=PesquisaPrecoForm,
    extra=1,
    can_delete=True
)


# 5. Formulário para Status do ETP
class ETPStatusForm(forms.ModelForm):
    class Meta:
        model = ETP
        fields = ['status', 'observacoes_analise']
        widgets = {
            'observacoes_analise': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'observacoes_analise' and field_name != 'status' and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput, forms.EmailInput, forms.URLInput)):
                field.widget.attrs.update({'class': 'form-control'})


# 6. Formulário para TR (Termo de Referência)
class TRForm(forms.ModelForm):
    class Meta:
        model = TR
        fields = '__all__'
        widgets = {
            'objeto': CKEditorWidget(attrs={'class': 'form-control'}),
            'justificativa': CKEditorWidget(attrs={'class': 'form-control'}),
            'especificacoes_tecnicas': CKEditorWidget(attrs={'class': 'form-control'}),
            'metodologia_execucao': CKEditorWidget(attrs={'class': 'form-control'}),
            'cronograma_fisico_financeiro': CKEditorWidget(attrs={'class': 'form-control'}),
            'criterios_habilitacao': CKEditorWidget(attrs={'class': 'form-control'}),
            'criterios_aceitacao': CKEditorWidget(attrs={'class': 'form-control'}),
            'criterios_pagamento': CKEditorWidget(attrs={'class': 'form-control'}),
            'obrigacoes_partes': CKEditorWidget(attrs={'class': 'form-control'}),
            'sancoes_administrativas': CKEditorWidget(attrs={'class': 'form-control'}),
            'fiscalizacao_contrato': CKEditorWidget(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.etp_origem_instance = kwargs.pop('etp_origem', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if not isinstance(field.widget, CKEditorWidget) and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput, forms.EmailInput, forms.URLInput)):
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        etp = self.etp_origem_instance 

        if etp and etp.requisitos_contratacao and not cleaned_data.get('especificacoes_tecnicas'):
            self.add_error('especificacoes_tecnicas', 'Campo "Especificações Técnicas" é obrigatório, pois o ETP de origem possui requisitos de contratação.')

        return cleaned_data

# 7. Formulário para Anexo
# class AnexoForm(forms.ModelForm):
#     class Meta:
#         model = Anexo
#         fields = ['titulo', 'arquivo']
#         widgets = {
#             'titulo': forms.TextInput(attrs={'class': 'form-control'}),
#             'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             if field_name not in self.Meta.widgets and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput, forms.EmailInput, forms.URLInput, forms.FileInput)):
#                 field.widget.attrs.update({'class': 'form-control'})


# 8. Formulário para Status do TR
class TRStatusForm(forms.ModelForm):
    class Meta:
        model = TR
        fields = ['status', 'observacoes_analise']
        widgets = {
            'observacoes_analise': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'observacoes_analise' and field_name != 'status' and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput, forms.EmailInput, forms.URLInput)):
                field.widget.attrs.update({'class': 'form-control'})

# --- Formulários para PCA e ItemPCA (pertencem a 'contratacoes') ---

# 9. Formulário para PCA
class PCAForm(forms.ModelForm):
    class Meta:
        model = PCA
        fields = ['ano_vigencia', 'titulo', 'descricao', 'data_aprovacao', 'responsavel_aprovacao', 'arquivo_pca'] 
        widgets = {
            'ano_vigencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'data_aprovacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'responsavel_aprovacao': forms.Select(attrs={'class': 'form-control'}),
            'arquivo_pca': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'ano_vigencia': 'Ano de Vigência',
            'titulo': 'Título do PCA',
            'descricao': 'Descrição do PCA',
            'data_aprovacao': 'Data de Aprovação do PCA',
            'responsavel_aprovacao': 'Responsável pela Aprovação',
            'arquivo_pca': 'Arquivo PCA Completo (PDF)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput, forms.EmailInput, forms.URLInput, forms.FileInput)):
                field.widget.attrs.update({'class': 'form-control'})

# 10. Formulário para ItemPCA
class ItemPCAForm(forms.ModelForm):
    class Meta:
        model = ItemPCA
        fields = ['pca', 'identificador_item', 'descricao_item', 'valor_estimado_pca', 'unidade_requisitante'] 
        widgets = {
            'pca': forms.Select(attrs={'class': 'form-control'}),
            'identificador_item': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_item': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'valor_estimado_pca': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidade_requisitante': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'pca': 'Plano de Contratações Anual',
            'identificador_item': 'Identificador do Item',
            'descricao_item': 'Descrição do Item',
            'valor_estimado_pca': 'Valor Estimado no PCA (R$)',
            'unidade_requisitante': 'Unidade Requisitante',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in self.Meta.widgets and isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput, forms.EmailInput, forms.URLInput)):
                field.widget.attrs.update({'class': 'form-control'})
