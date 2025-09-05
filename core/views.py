# SysGov_Project/core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse # Para retornar o HTML para AJAX
from django.template.loader import render_to_string # Para renderizar templates como string
from django.contrib import messages
from django.db.models.functions import TruncMonth
# Importações dos modelos e formulários do próprio app 'core'
from .models import Processo, ArquivoAnexo
from .forms import ProcessoForm, ArquivoAnexoForm
from django.db.models import Sum, Count, F, Func
# Importe os modelos necessários dos outros apps (agora que estão no mesmo projeto)
from contratacoes.models import ETP, TR
from licitacoes.models import Edital
from financeiro.models import DocumentoFiscal, Pagamento
from django.contrib.contenttypes.models import ContentType

from contratacoes.models import Contrato, ETP
from licitacoes.models import Edital, ResultadoLicitacao
from financeiro.models import Pagamento

# views.py (apenas para teste temporário)
import os
from django.conf import settings # Importar settings para acessar STATIC_ROOT ou MEDIA_ROOT

# core/views.py
import os
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404


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
    

def home(request):
    dashboard_stats = {}
    # Nomes para o novo gráfico de status
    labels_status = []
    data_status = []

    if request.user.is_authenticated:
        # Estatísticas gerais (já existentes)
        dashboard_stats = {
            'processos_em_analise': Processo.objects.filter(status='EM_ANALISE').count(),
            'licitacoes_abertas': Edital.objects.filter(status='ABERTO').count(),
            'contratos_vigentes': Contrato.objects.filter(status='VIGENTE').count(),
        }
        
        # --- NOVA LÓGICA PARA O GRÁFICO DE STATUS ---
        # Agrupa os ETPs por status e conta quantos há em cada um
        status_data = ETP.objects.values('status') \
            .annotate(count=Count('id')) \
            .order_by('status')

        # Cria um dicionário para traduzir o código do status (ex: 'EM_ELABORACAO') para o nome legível
        status_display_map = dict(ETP._meta.get_field('status').choices)

        labels_status = [status_display_map.get(item['status'], item['status']) for item in status_data]
        data_status = [item['count'] for item in status_data]

    context = {
        'dashboard_stats': dashboard_stats,
        'labels_status': labels_status,
        'data_status': data_status,
    }
    return render(request, 'core/home.html', context)

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



from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import Processo, ArquivoAnexo

# Importe os modelos dos outros apps para poder encontrá-los
from contratacoes.models import ETP, TR, Contrato
from licitacoes.models import Edital

@login_required(login_url='/accounts/login/')
def detalhes_processo_view(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id)
    
    # Busca o ETP associado (se existir)
    try:
        etp = processo.etp_documento
    except ETP.DoesNotExist:
        etp = None

    # Busca o TR associado (se existir)
    try:
        tr = processo.tr_documento
    except TR.DoesNotExist:
        tr = None
        
    # Busca o Edital associado (se existir)
    try:
        # Nota: 'edital_licitacao' é um exemplo de related_name. Ajuste se o seu for diferente.
        edital = processo.edital_licitacao
    except Edital.DoesNotExist:
        edital = None

    # Busca TODOS os contratos vinculados a este processo
    contratos = processo.contratos.all()

    # Busca os anexos genéricos do processo
    processo_content_type = ContentType.objects.get_for_model(Processo)
    anexos_do_processo = ArquivoAnexo.objects.filter(
        content_type=processo_content_type,
        object_id=processo.id
    ).order_by('-data_upload')

    context = {
        'processo': processo,
        'etp': etp,
        'tr': tr,
        'edital': edital,
        'contratos': contratos,
        'anexos_do_processo': anexos_do_processo,
        'titulo_pagina': f"Painel do Processo {processo.numero_protocolo or ''}"
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

# Em core/views.py
from .forms import FornecedorForm # Adicione esta importação
from .models import Fornecedor    # Adicione esta importação

# ... (outras views) ...

@login_required
def listar_fornecedores(request):
    fornecedores = Fornecedor.objects.all().order_by('razao_social')
    context = {
        'fornecedores': fornecedores,
        'titulo_pagina': 'Cadastro de Fornecedores'
    }
    return render(request, 'core/listar_fornecedores.html', context)

@login_required
def criar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('listar_fornecedores')
    else:
        form = FornecedorForm()

    context = {
        'form': form,
        'titulo_pagina': 'Cadastrar Novo Fornecedor'
    }
    return render(request, 'core/criar_fornecedor.html', context)


# Em core/views.py

@login_required
def detalhar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    # Buscamos os contratos e empenhos relacionados a este fornecedor
    contratos = fornecedor.contratos.all()
    empenhos = fornecedor.empenhos.all()
    context = {
        'fornecedor': fornecedor,
        'contratos': contratos,
        'empenhos': empenhos,
        'titulo_pagina': f'Detalhes de {fornecedor.razao_social}'
    }
    return render(request, 'core/detalhar_fornecedor.html', context)


# Em core/views.py

@login_required
def editar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados do fornecedor atualizados com sucesso!')
            return redirect('detalhar_fornecedor', pk=fornecedor.pk)
    else:
        form = FornecedorForm(instance=fornecedor)

    context = {
        'form': form,
        'fornecedor': fornecedor,
        'titulo_pagina': 'Editar Fornecedor'
    }
    return render(request, 'core/editar_fornecedor.html', context)



@login_required
def dashboard_gerencial_view(request):
    """
    Coleta e prepara os dados para o dashboard gerencial com múltiplos gráficos.
    """
    # --- Gráfico 1: Distribuição de ETPs por Status ---
    status_data = ETP.objects.values('status').annotate(count=Count('id')).order_by('status')
    status_display_map = dict(ETP._meta.get_field('status').choices)
    labels_status = [status_display_map.get(item['status'], item['status']) for item in status_data]
    data_status = [item['count'] for item in status_data]

    # --- Gráfico 2: Top 5 Fornecedores por Valor Contratado ---
    top_fornecedores_data = Contrato.objects.values('contratado__razao_social') \
        .annotate(total_valor=Sum('valor_total')) \
        .order_by('-total_valor')[:5]
    labels_fornecedores = [item['contratado__razao_social'] for item in top_fornecedores_data]
    data_fornecedores = [float(item['total_valor']) for item in top_fornecedores_data]

    # --- Gráfico 3: Economia Média Mensal em Licitações ---
    economia_mensal_data = ResultadoLicitacao.objects.filter(
        valor_estimado_inicial__isnull=False, 
        valor_homologado__isnull=False
    ).annotate(mes=TruncMonth('data_homologacao')) \
     .values('mes') \
     .annotate(
        economia_total=Sum(F('valor_estimado_inicial') - F('valor_homologado')),
        num_licitacoes=Count('id')
     ).order_by('mes')
    
    labels_economia = [item['mes'].strftime('%b/%Y') for item in economia_mensal_data]
    data_economia = []
    for item in economia_mensal_data:
        if item['num_licitacoes'] > 0:
            data_economia.append(float(item['economia_total'] / item['num_licitacoes']))
        else:
            data_economia.append(0)

    context = {
        'titulo_pagina': 'Dashboard Gerencial',
        'labels_status': labels_status,
        'data_status': data_status,
        'labels_fornecedores': labels_fornecedores,
        'data_fornecedores': data_fornecedores,
        'labels_economia': labels_economia,
        'data_economia': data_economia,
    }
    return render(request, 'core/dashboard_gerencial.html', context)