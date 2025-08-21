# SysGov_Project/core/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm # Mantenha se precisar de CustomAuthenticationForm, senão pode remover
from .models import Processo , ArquivoAnexo


# Formulário para a criação de um novo Processo
class ProcessoForm(forms.ModelForm):
    class Meta:
        model = Processo
        # Campos que o usuário poderá preencher no formulário
        # Excluímos 'usuario', 'status', 'data_criacao', 'data_atualizacao'
        # porque eles serão preenchidos automaticamente na view.
        fields = ['titulo', 'descricao', 'numero_protocolo']
        # Definir labels amigáveis para os campos no formulário
        labels = {
            'titulo': 'Título/Assunto do Processo',
            'descricao': 'Descrição Detalhada',
            'numero_protocolo': 'Número de Protocolo (Opcional)',
        }
        # Adicionar classes Bootstrap aos campos de entrada
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Contratação de Software X, Pedido de Licença Ambiental'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalhe o motivo e a necessidade deste processo...'}),
            'numero_protocolo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2025/001-PMB'}),
        }

# Mantenha CustomAuthenticationForm se precisar dela para outras finalidades,
# senão você pode remover esta classe.
class CustomAuthenticationForm(AuthenticationForm):
    pass



from django import forms
from .models import Processo, ArquivoAnexo # Importa o modelo ArquivoAnexo

# ... (Seu ProcessoForm existente) ...

class ArquivoAnexoForm(forms.ModelForm):
    class Meta:
        model = ArquivoAnexo
        fields = ['titulo', 'arquivo'] # O uploaded_by e o vínculo serão preenchidos na view
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ata de Homologação, Parecer Jurídico'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}), # Input para arquivo
        }
        labels = {
            'titulo': 'Título do Anexo',
            'arquivo': 'Selecione o Arquivo',
        }

# ... (Seu CustomAuthenticationForm existente, se houver) ...