# core/forms.py
from django import forms
# Não precisa de inlineformset_factory aqui
# Importe os modelos originais
from .models import DocumentoFiscal, Pagamento

# Formulário para o Documento Fiscal (como estava antes do formset)
class DocumentoFiscalForm(forms.ModelForm):
    class Meta:
        model = DocumentoFiscal # Volta a usar DocumentoFiscal
        fields = '__all__'
        widgets = {
            'codigo_ajuste': forms.TextInput(attrs={'class': 'form-control'}),
            'medicao_numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'nota_empenho_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'nota_empenho_data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'documento_fiscal_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_fiscal_uf': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_fiscal_valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'documento_fiscal_data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'codigo_ajuste': "Código do Ajuste/Empenho",
            'medicao_numero': "Número da Medição",
            'nota_empenho_numero': "Número da Nota de Empenho",
            'nota_empenho_data_emissao': "Data de Emissão da Nota de Empenho",
            'documento_fiscal_numero': "Número do Documento Fiscal (NF)",
            'documento_fiscal_uf': "UF do Documento Fiscal (Ex: SP)",
            'documento_fiscal_valor': "Valor do Documento Fiscal",
            'documento_fiscal_data_emissao': "Data de Emissão do Documento Fiscal",
        }

# O PagamentoForm permanece o mesmo
class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = '__all__'
        widgets = {
            'codigo_ajuste': forms.TextInput(attrs={'class': 'form-control'}),
            'medicao_numero': forms.NumberInput(attrs={'class': 'form-control'}),
            'nota_empenho_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'nota_empenho_data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'documento_fiscal_numero': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_fiscal_data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'documento_fiscal_uf': forms.TextInput(attrs={'class': 'form-control'}),
            'nota_fiscal_valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'nota_fiscal_pagto_dt': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'recolhido_encargos_previdenciario': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'codigo_ajuste': "Código do Ajuste/Empenho",
            'medicao_numero': "Número da Medição",
            'nota_empenho_numero': "Número da Nota de Empenho",
            'nota_empenho_data_emissao': "Data de Emissão da Nota de Empenho",
            'documento_fiscal_numero': "Número do Documento Fiscal (NF)",
            'documento_fiscal_data_emissao': "Data de Emissão do Documento Fiscal",
            'documento_fiscal_uf': "UF do Documento Fiscal (Ex: SP)",
            'nota_fiscal_valor_pago': "Valor Pago da Nota Fiscal",
            'nota_fiscal_pagto_dt': "Data Efetiva do Pagamento",
            'recolhido_encargos_previdenciario': "Recolhido Encargos Previdenciários?",
        }