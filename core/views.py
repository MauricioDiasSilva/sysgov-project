# SysGov_Project/core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse # Para retornar o HTML para AJAX
from django.template.loader import render_to_string # Para renderizar templates como string
from django.contrib import messages

# Importações dos modelos e formulários do próprio app 'core'
from .models import Processo, ArquivoAnexo
from .forms import ProcessoForm, ArquivoAnexoForm

# Importe os modelos necessários dos outros apps (agora que estão no mesmo projeto)
from contratacoes.models import ETP, TR
from licitacoes.models import Edital
from financeiro.models import DocumentoFiscal, Pagamento
from django.contrib.contenttypes.models import ContentType

# views.py (apenas para teste temporário)
import os
from django.conf import settings # Importar settings para acessar STATIC_ROOT ou MEDIA_ROOT

# core/views.py
import os
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from .models import ArquivoAnexo # Certifique-se de que ArquivoAnexo está importado

def visualizar_anexo_pdf(request, anexo_id):
    anexo = get_object_or_404(ArquivoAnexo, pk=anexo_id)
    
    # !!! VERIFIQUE SE O CAMPO 'arquivo' NO SEU MODELO ArquivoAnexo TEM UM VALOR !!!
    # Se 'arquivo' for um FileField e estiver vazio para este anexo, anexo.arquivo pode ser None.
    if not anexo.arquivo: 
        raise Http404("Arquivo PDF não anexado para este item.")

    file_path = anexo.arquivo.path # Este é o caminho completo do arquivo no sistema de arquivos
    
    # Adicione este print para depuração (vai aparecer no terminal do Django)
    print(f"Tentando abrir arquivo em: {file_path}")

    if not os.path.exists(file_path):
        # Se o arquivo não existir no disco, é um 404
        raise Http404("O arquivo não existe no sistema de arquivos do servidor.")

    # Verifica se o arquivo é um PDF antes de tentar servi-lo como tal
    # Isso é opcional, mas ajuda a evitar erros se for outro tipo de arquivo
    if not anexo.arquivo.name.lower().endswith('.pdf'):
         return HttpResponse("Este arquivo não é um PDF.", status=400) # Bad Request

    with open(file_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        # Opcional: Adicione um cabeçalho para nomear o arquivo no download
        # response['Content-Disposition'] = f'inline; filename="{anexo.arquivo.name}"' # 'inline' para abrir no navegador, 'attachment' para baixar
        return response
    



def home_view(request):
    # Você pode adicionar dados aqui para o dashboard, se precisar.
    # Por enquanto, o dashboard usa apenas user.is_authenticated para exibir botões.
    return render(request, 'core/home.html')

# ... (suas outras views)
# View para a página "Meus Processos"
@login_required(login_url='/accounts/login/')
def meus_processos_view(request):
    processos = Processo.objects.filter(usuario=request.user)
    context = {
        'processos': processos,
        'usuario_atual': request.user.username
    }
    return render(request, 'core/meus_processos.html', context)

# View para Criar um Novo Processo
@login_required(login_url='/accounts/login/')
def criar_processo_view(request):
    if request.method == 'POST':
        form = ProcessoForm(request.POST)
        if form.is_valid():
            processo = form.save(commit=False)
            processo.usuario = request.user
            processo.save()
            messages.success(request, 'Processo criado com sucesso!')
            return redirect('meus_processos')
    else:
        form = ProcessoForm()
    context = {
        'form': form,
        'titulo_pagina': 'Criar Novo Processo'
    }
    return render(request, 'core/criar_processo.html', context)

# SysGov_Project/core/views.py

@login_required(login_url='/accounts/login/')
def detalhes_processo_view(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id)
    
    # <<< ATENÇÃO: BUSCA CORRETA DOS ARQUIVOANEXO VINCULADOS AO PROCESSO >>>
    # Obtenha o ContentType do modelo Processo
    processo_content_type = ContentType.objects.get_for_model(Processo)
    
    # Filtra ArquivoAnexo onde content_type é o de Processo e object_id é o ID do Processo atual
    anexos_do_processo = ArquivoAnexo.objects.filter(
        content_type=processo_content_type,
        object_id=processo.id
    ).order_by('-data_upload') # Ordenar os anexos pelo mais recente

    context = {
        'processo': processo,
        'titulo_pagina': f'Detalhes do Processo {processo.numero_protocolo if processo.numero_protocolo else "N/A"}',
        'anexos_do_processo': anexos_do_processo, # <<< PASSA A LISTA DE ANEXOS AO TEMPLATE
    }
    return render(request, 'core/detalhes_processo.html', context)


# View para Adicionar Anexo a um Processo
@login_required(login_url='/accounts/login/')
def adicionar_anexo_ao_processo(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id)
    
    if request.method == 'POST':
        form = ArquivoAnexoForm(request.POST, request.FILES)
        if form.is_valid():
            anexo = form.save(commit=False)
            anexo.uploaded_by = request.user
            anexo.content_object = processo
            anexo.save()
            messages.success(request, 'Anexo adicionado ao processo com sucesso!')
            return redirect('detalhes_processo', processo_id=processo.id)
        else:
            messages.error(request, 'Erro ao adicionar anexo. Verifique o formulário.')
    else: # GET request
        form = ArquivoAnexoForm()
    
    # <<< AJUSTE AQUI: Use lógica Python para o valor padrão >>>
    numero_protocolo_display = processo.numero_protocolo if processo.numero_protocolo else "N/A" # <<< ESTA LINHA FOI ADICIONADA/AJUSTADA
    
    context = {
        'form': form,
        'processo': processo,
        'titulo_pagina': f'Adicionar Anexo ao Processo {numero_protocolo_display}' # <<< Use a variável ajustada
    }
    return render(request, 'core/adicionar_anexo_processo.html', context)


# --- VIEWS PARA RENDERIZAR SNIPPETS DE DOCUMENTOS VIA AJAX ---
# Estas views retornam apenas o HTML dos detalhes de um documento para a visualização dinâmica
@login_required
def render_etp_detail_snippet(request, pk):
    etp = get_object_or_404(ETP, pk=pk)
    if etp.processo_vinculado and etp.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este ETP.", status=403)
    
    html_content = render_to_string('core/snippets/etp_detail_snippet.html', {'etp': etp, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_tr_detail_snippet(request, pk):
    tr = get_object_or_404(TR, pk=pk)
    if tr.processo_vinculado and tr.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este TR.", status=403)
    
    html_content = render_to_string('core/snippets/tr_detail_snippet.html', {'tr': tr, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_edital_detail_snippet(request, pk):
    edital = get_object_or_404(Edital, pk=pk)
    if edital.processo_vinculado and edital.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este Edital.", status=403)
    
    html_content = render_to_string('core/snippets/edital_detail_snippet.html', {'edital': edital, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_df_detail_snippet(request, pk):
    df = get_object_or_404(DocumentoFiscal, pk=pk)
    if df.processo_vinculado and df.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este Documento Fiscal.", status=403)
        
    html_content = render_to_string('core/snippets/df_detail_snippet.html', {'df': df, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_pagamento_detail_snippet(request, pk):
    pg = get_object_or_404(Pagamento, pk=pk)
    if pg.processo_vinculado and pg.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este Pagamento.", status=403)
        
    html_content = render_to_string('core/snippets/pagamento_detail_snippet.html', {'pagamento': pg, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_arquivo_anexo_detail_snippet(request, pk):
    anexo = get_object_or_404(ArquivoAnexo, pk=pk)
    # GFK: Verifique se o processo vinculado ao anexo pertence ao usuário logado
    # Esta verificação é importante para segurança.
    if anexo.content_type.model == 'processo' and anexo.content_object.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este anexo.", status=403)
    
    # <<< AJUSTE AQUI: Passe o 'request' ao render_to_string >>>
    html_content = render_to_string('core/snippets/arquivo_anexo_detail_snippet.html', {'anexo': anexo}, request=request)
    return HttpResponse(html_content)



