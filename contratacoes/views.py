# SysGov_Project/contratacoes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Count, Q, F # Manter Q se for usar para queries mais complexas
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
from django.db import transaction
import json
from weasyprint import HTML
from core.forms import ArquivoAnexoForm
from decimal import Decimal # Necessário para cálculos com DecimalField
from . import ai_services
# Importação crucial do modelo Processo e ArquivoAnexo do app 'core'
from core.models import Processo, ArquivoAnexo # <<< Importação corrigida para ArquivoAnexo
from django.forms import inlineformset_factory
# Importar os modelos da sua própria app 'contratacoes'
from .models import (
    ETP, TR, PCA, ItemPCA, PesquisaPreco, ParecerTecnico,AtaRegistroPrecos,
    ModeloTexto, RequisitoPadrao, ItemCatalogo, STATUS_DOCUMENTO_CHOICES,Contrato 
)

from .forms import (
    ETPForm, TRForm, PesquisaPrecoForm,
    ParecerTecnicoForm, ETPStatusForm, 
    # PesquisaPrecoFormSet,  <<< REMOVIDO DESTA IMPORTAÇÃO
    TRStatusForm,
    PCAForm, ItemPCAForm,
    ItemCatalogoForm
)

# DEFINIÇÃO DOS FORMSETS - O LUGAR CORRETO É AQUI!
PesquisaPrecoFormSet = inlineformset_factory(ETP, PesquisaPreco, form=PesquisaPrecoForm, extra=1, can_delete=True)
ParecerTecnicoFormSet = inlineformset_factory(ETP, ParecerTecnico, form=ParecerTecnicoForm, extra=1, can_delete=True)
ItemPCAFormSet = inlineformset_factory(PCA, ItemPCA, form=ItemPCAForm, extra=1, can_delete=True)

@login_required
def listar_catalogo_itens(request):
    itens = ItemCatalogo.objects.all().order_by('nome_padronizado')
    context = {
        'itens': itens,
        'titulo_pagina': 'Catálogo de Itens Padronizados',
    }
    return render(request, 'contratacoes/listar_catalogo_itens.html', context)

@login_required
def criar_item_catalogo(request): # <<< VIEW COMPLETA
    if request.method == 'POST':
        form = ItemCatalogoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item de Catálogo criado com sucesso!')
            return redirect('contratacoes:listar_catalogo_itens')
        else:
            messages.error(request, 'Erro ao criar Item de Catálogo. Verifique o formulário.')
    else: # GET request
        form = ItemCatalogoForm()

    context = {
        'form': form,
        'titulo_pagina': 'Criar Novo Item de Catálogo',
    }
    return render(request, 'contratacoes/criar_item_catalogo.html', context)




# SysGov_Project/contratacoes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Avg, Count, Q, F
# ... (outros imports) ...

# Em SysGov_Project/contratacoes/views.py

from django.db.models import Q # <<< Adicione esta importação no topo se não existir

# ... (outras views) ...

@login_required 
def listar_etps(request):
    # Inicia o queryset base. Nenhum ETP por padrão, a menos que uma regra se aplique.
    etps_base = ETP.objects.none()

    # Verifica os grupos do usuário para aplicar as regras de visualização
    is_secretaria = request.user.groups.filter(name='Secretarias').exists()
    is_analise = request.user.groups.filter(name='Analise de Requerimentos').exists()
    is_orcamento = request.user.groups.filter(name='Setor de Orcamento').exists()
    
    # REGRA 1: Superusuários veem tudo.
    if request.user.is_superuser:
        etps_base = ETP.objects.all()
    
    # REGRA 2: Usuários de Secretarias veem apenas os ETPs que eles criaram.
    elif is_secretaria:
        etps_base = ETP.objects.filter(autor=request.user)
        
    # REGRA 3: Pessoal da Análise vê o que está aguardando análise ou o que eles já manipularam.
    elif is_analise:
        etps_base = ETP.objects.filter(
            Q(status='AGUARDANDO_ANALISE') | 
            Q(status='RECUSADO_ANALISE') | 
            Q(status='AGUARDANDO_ORCAMENTO') |
            Q(status='APROVADO')
        )

    # REGRA 4: Pessoal do Orçamento vê o que está aguardando orçamento ou o que eles já manipularam.
    elif is_orcamento:
        etps_base = ETP.objects.filter(
            Q(status='AGUARDANDO_ORCAMENTO') |
            Q(status='RECUSADO_ORCAMENTO') |
            Q(status='APROVADO')
        )
    
    # Opcional: Se um usuário não pertence a nenhum grupo específico, ele só vê o que criou.
    else:
        etps_base = ETP.objects.filter(autor=request.user)

    # Mantemos o filtro de status que já existia na URL
    status_filtro = request.GET.get('status') 
    if status_filtro:
        etps_filtrados = etps_base.filter(status=status_filtro)
    else:
        etps_filtrados = etps_base
    
    context = {
        'etps': etps_filtrados.order_by('-data_criacao'),
        'titulo_pagina': 'Lista de ETPs',
        'status_filtro': status_filtro,
    }
    return render(request, 'contratacoes/listar_etps.html', context)


@login_required
def criar_etp(request, processo_id=None):
    processo_core = None
    if processo_id:
        processo_core = get_object_or_404(Processo, id=processo_id)
        if hasattr(processo_core, 'etp_documento'):
            messages.info(request, "Este processo já possui um ETP. Você será redirecionado para editá-lo.")
            return redirect('contratacoes:detalhar_etp', pk=processo_core.etp_documento.pk)

    dados_iniciais = request.session.pop('dados_etp_ia', {})

    if request.method == 'POST':
        print("--- DENTRO DO POST ---")
        form = ETPForm(request.POST)
        pesquisas_formset = PesquisaPrecoFormSet(request.POST, prefix='pesquisas')
        pareceres_formset = ParecerTecnicoFormSet(request.POST, prefix='pareceres')

        form_valido = form.is_valid()
        pesquisas_valido = pesquisas_formset.is_valid()
        pareceres_valido = pareceres_formset.is_valid()

        print(f"Formulário principal é válido? {form_valido}")
        print(f"Formset de Pesquisas é válido? {pesquisas_valido}")
        print(f"Formset de Pareceres é válido? {pareceres_valido}")

        if not pareceres_valido:
            print("--- ERROS NO FORMSET DE PARECERES ---")
            print(pareceres_formset.errors)

        if form_valido and pesquisas_valido and pareceres_valido:
            print("--- TUDO VÁLIDO, TENTANDO SALVAR ---")
            try:
                with transaction.atomic():
                    etp = form.save(commit=False)
                    etp.autor = request.user
                    if processo_core:
                        etp.processo_vinculado = processo_core
                    etp.save()
                    
                    pesquisas_formset.instance = etp
                    pesquisas_formset.save()
                    
                    pareceres_formset.instance = etp
                    pareceres_formset.save()

                    messages.success(request, 'ETP criado com sucesso!')
                    if processo_core:
                        return redirect('detalhes_processo', processo_id=processo_core.id)
                    else:
                        return redirect('contratacoes:detalhar_etp', pk=etp.pk)
            except Exception as e:
                # <<< ADICIONAMOS ESTE ESPIÃO PARA VER O ERRO OCULTO >>>
                print(f"!!!!!!!!!! ERRO AO SALVAR NO BANCO DE DADOS: {e} !!!!!!!!!!!")
                messages.error(request, f"Ocorreu um erro inesperado ao salvar: {e}")

        else:
            messages.error(request, 'Erro de validação. Verifique os campos.')
    else:
        form = ETPForm(initial=dados_iniciais)
        pesquisas_formset = PesquisaPrecoFormSet(prefix='pesquisas')
        pareceres_formset = ParecerTecnicoFormSet(prefix='pareceres')

    context = {
        'form': form,
        'pesquisas_formset': pesquisas_formset,
        'pareceres_formset': pareceres_formset,
        'processo_core': processo_core,
        'titulo_pagina': 'Criar Novo ETP',
    }
    return render(request, 'contratacoes/criar_etp.html', context)

@login_required
def detalhar_etp(request, pk):
    etp = get_object_or_404(ETP, pk=pk)
    # Garante que o usuário logado só pode ver seus próprios ETPs, a menos que seja superuser
    if etp.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para visualizar este ETP.')
        return redirect('contratacoes:listar_etps')

    pendencias_analise = etp.get_analise_preliminar() # Chama o método de análise do modelo

    context = {
        'etp': etp,
        'titulo_pagina': f'Detalhes do ETP: {etp.titulo}',
        'pendencias_analise': pendencias_analise,
        'status_choices': STATUS_DOCUMENTO_CHOICES # Passar as escolhas de status para o template
    }
    return render(request, 'contratacoes/detalhar_etp.html', context)

# Em SysGov_Project/contratacoes/views.py

@login_required
def editar_etp(request, pk):
    etp = get_object_or_404(ETP, pk=pk)

    # Lógica de permissão
    if etp.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para editar este ETP.')
        return redirect('contratacoes:detalhar_etp', pk=etp.pk)

    if request.method == 'POST':
        form = ETPForm(request.POST, instance=etp)
        # <<< ALINHAMENTO AQUI: Criamos os formsets também no POST >>>
        pesquisas_formset = PesquisaPrecoFormSet(request.POST, instance=etp, prefix='pesquisas')
        pareceres_formset = ParecerTecnicoFormSet(request.POST, instance=etp, prefix='pareceres')

        if form.is_valid() and pesquisas_formset.is_valid() and pareceres_formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    pesquisas_formset.save()
                    pareceres_formset.save()
                    messages.success(request, 'ETP atualizado com sucesso!')
                    return redirect('contratacoes:detalhar_etp', pk=etp.pk)
            except Exception as e:
                print(f"!!!!!!!!!! ERRO AO SALVAR NA EDIÇÃO: {e} !!!!!!!!!!!")
                messages.error(request, f"Ocorreu um erro inesperado ao salvar: {e}")
        else:
            messages.error(request, 'Erro ao atualizar ETP. Verifique os campos.')
            print("ERROS (EDIÇÃO):", form.errors, pesquisas_formset.errors, pareceres_formset.errors)

    else: # GET request
        form = ETPForm(instance=etp)
        pesquisas_formset = PesquisaPrecoFormSet(instance=etp, prefix='pesquisas')
        pareceres_formset = ParecerTecnicoFormSet(instance=etp, prefix='pareceres')

    context = {
        'form': form,
        'pesquisas_formset': pesquisas_formset,
        'pareceres_formset': pareceres_formset,
        'etp': etp,
        'titulo_pagina': f'Editar ETP: {etp.titulo}',
    }
    return render(request, 'contratacoes/editar_etp.html', context)


@login_required
def atualizar_status_etp(request, pk):
    etp = get_object_or_404(ETP, pk=pk)


    if request.method == 'POST':
        form = ETPStatusForm(request.POST, instance=etp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status do ETP atualizado com sucesso!')
            return redirect('contratacoes:detalhar_etp', pk=etp.pk)
        else:
            messages.error(request, 'Erro ao atualizar status. Verifique o formulário.')
    # Se não for POST ou se o formulário não for válido, renderiza com o formulário de status
    return redirect('contratacoes:detalhar_etp', pk=etp.pk) # Redireciona de volta para a página de detalhes, que exibirá o formulário de status

# Em SysGov_Project/contratacoes/views.py

# ... (outras views) ...

@login_required
def listar_trs(request):
    # Inicia com uma lista vazia
    trs_base = TR.objects.none()

    # Verifica os grupos do usuário
    is_secretaria = request.user.groups.filter(name='Secretarias').exists()
    # Para o TR, vamos considerar que tanto a Análise quanto o Orçamento precisam ver os TRs em andamento
    is_analista_ou_orcamento = request.user.groups.filter(name__in=['Analise de Requerimentos', 'Setor de Orcamento']).exists()

    # REGRA 1: Superusuários veem tudo.
    if request.user.is_superuser:
        trs_base = TR.objects.all()
    
    # REGRA 2: Pessoal de Análise e Orçamento veem todos os TRs que não estão mais em elaboração.
    elif is_analista_ou_orcamento:
        trs_base = TR.objects.exclude(status='EM_ELABORACAO')

    # REGRA 3: Usuários de Secretarias (e outros sem grupo especial) veem apenas os que eles criaram.
    else:
        trs_base = TR.objects.filter(autor=request.user)
        
    context = {
        'trs': trs_base.order_by('-data_criacao'),
        'titulo_pagina': 'Lista de Termos de Referência',
    }
    return render(request, 'contratacoes/listar_trs.html', context)

# SysGov_Project/contratacoes/views.py

@login_required
def criar_tr(request, etp_id=None, processo_id=None):
    etp_origem = None
    processo_core = None

    # Sua lógica para encontrar o ETP ou o Processo (MANTIDA, ESTÁ PERFEITA)
    if etp_id:
        etp_origem = get_object_or_404(ETP, id=etp_id)
        if hasattr(etp_origem, 'termo_referencia'):
            messages.info(request, "Este ETP já possui um TR. Você será redirecionado para editá-lo.")
            return redirect('contratacoes:editar_tr', pk=etp_origem.termo_referencia.pk)
        if etp_origem.processo_vinculado:
            processo_core = etp_origem.processo_vinculado
    elif processo_id:
        processo_core = get_object_or_404(Processo, id=processo_id)
        if hasattr(processo_core, 'tr_documento'):
            messages.info(request, "Este processo já possui um TR. Você será redirecionado para editá-lo.")
            return redirect('contratacoes:editar_tr', pk=processo_core.tr_documento.pk)

    # Sua lógica de POST para salvar o formulário (MANTIDA, ESTÁ PERFEITA)
    if request.method == 'POST':
        form = TRForm(request.POST)
        if form.is_valid():
            tr = form.save(commit=False)
            tr.autor = request.user
            if etp_origem:
                tr.etp_origem = etp_origem
            if processo_core:
                tr.processo_vinculado = processo_core
            tr.save()
            messages.success(request, 'Termo de Referência criado com sucesso!')
            return redirect('contratacoes:detalhar_tr', pk=tr.pk)
        else:
            messages.error(request, 'Erro ao criar Termo de Referência. Verifique os campos.')
            
    # LÓGICA DE GET ATUALIZADA PARA INCLUIR A IA
    else: 
        # 1. Primeiro, tentamos pegar os dados pré-preenchidos pela IA da sessão.
        dados_iniciais = request.session.pop('dados_tr_ia', {})

        # 2. Em seguida, usamos a sua lógica para completar com os outros dados.
        if etp_origem:
            # Atualiza o dicionário, adicionando ou substituindo chaves
            dados_iniciais.update({
                'titulo': f"TR do ETP: {etp_origem.titulo}",
                'numero_processo': etp_origem.numero_processo,
                'estimativa_preco_tr': etp_origem.estimativa_valor
            })
            # Se a IA não preencheu, usamos os dados do ETP como fallback
            dados_iniciais.setdefault('justificativa', etp_origem.descricao_necessidade)
            dados_iniciais.setdefault('objeto', etp_origem.objetivo_contratacao)
        
        elif processo_core:
            dados_iniciais.update({
                'numero_processo': processo_core.numero_protocolo,
                'titulo': f"TR para processo: {processo_core.titulo}"
            })

        form = TRForm(initial=dados_iniciais)

    context = {
        'form': form,
        'etp_origem': etp_origem,
        'processo_core': processo_core,
        'titulo_pagina': 'Criar Termo de Referência',
    }
    return render(request, 'contratacoes/criar_tr.html', context)



@login_required
def detalhar_tr(request, pk):
    tr = get_object_or_404(TR, pk=pk)
    # Garante que o usuário logado só pode ver seus próprios TRs, a menos que seja superuser
    if tr.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para visualizar este TR.')
        return redirect('contratacoes:listar_trs')

    context = {
        'tr': tr,
        'titulo_pagina': f'Detalhes do TR: {tr.titulo}',
        'status_choices': STATUS_DOCUMENTO_CHOICES # Passar as escolhas de status para o template
    }
    return render(request, 'contratacoes/detalhar_tr.html', context)

@login_required
def editar_tr(request, pk):
    tr = get_object_or_404(TR, pk=pk)

    # Lógica de permissão e status:
    # Apenas o autor ou um superusuário pode editar
    if tr.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para editar este TR.')
        return redirect('contratacoes:detalhar_tr', pk=tr.pk)

    # Restrição de edição baseada no status (ex: não edita se já aprovado/recusado/cancelado)
    if tr.status in ['APROVADO', 'RECUSADO', 'CANCELADO'] and not request.user.is_superuser:
        messages.warning(request, f'Este TR está em status "{tr.get_status_display()}". Edições não são permitidas.')
        return redirect('contratacoes:detalhar_tr', pk=tr.pk)

    if request.method == 'POST':
        form = TRForm(request.POST, instance=tr)
        if form.is_valid():
            tr.save()
            messages.success(request, 'Termo de Referência atualizado com sucesso!')
            return redirect('contratacoes:detalhar_tr', pk=tr.pk)
        else:
            messages.error(request, 'Erro ao atualizar Termo de Referência. Verifique os campos.')
    else: # GET request
        form = TRForm(instance=tr)

    context = {
        'form': form,
        'tr': tr,
        'titulo_pagina': f'Editar TR: {tr.titulo}',
    }
    return render(request, 'contratacoes/editar_tr.html', context)

@login_required
def atualizar_status_tr(request, pk):
    tr = get_object_or_404(TR, pk=pk)
    # Lógica de permissão similar a ETP se necessário
    if request.method == 'POST':
        form = TRStatusForm(request.POST, instance=tr)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status do TR atualizado com sucesso!')
            return redirect('contratacoes:detalhar_tr', pk=tr.pk)
        else:
            messages.error(request, 'Erro ao atualizar status. Verifique o formulário.')
    return redirect('contratacoes:detalhar_tr', pk=tr.pk)


# --- VIEWS PARA PCA (Plano de Contratações Anual) ---
@login_required
def listar_pca(request):
    pcas = PCA.objects.all().order_by('-ano_vigencia')
    context = {
        'pcas': pcas,
        'titulo_pagina': 'Planos de Contratações Anuais (PCA)',
    }
    return render(request, 'contratacoes/listar_pcas.html', context)

# SysGov_Project/contratacoes/views.py

# ... (outras views de PCA)

@login_required
def adicionar_item_pca(request, pca_pk):
    pca = get_object_or_404(PCA, pk=pca_pk)

    # Opcional: Verificar permissão se o usuário pode adicionar itens a este PCA
    if pca.responsavel_aprovacao != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para adicionar itens a este PCA.')
        return redirect('contratacoes:detalhar_pca', pk=pca.pk)

    if request.method == 'POST':
        form = ItemPCAForm(request.POST)
        if form.is_valid():
            item_pca = form.save(commit=False)
            item_pca.pca = pca # Vincula o item ao PCA correto
            item_pca.save()
            messages.success(request, 'Item adicionado ao PCA com sucesso!')
            return redirect('contratacoes:detalhar_pca', pk=pca.pk)
        else:
            messages.error(request, 'Erro ao adicionar item. Verifique o formulário.')
    else:
        form = ItemPCAForm()

    context = {
        'form': form,
        'pca': pca,
        'titulo_pagina': f'Adicionar Item ao PCA {pca.ano_vigencia}'
    }
    return render(request, 'contratacoes/adicionar_item_pca.html', context) # Você precisará criar este template

@login_required
def criar_pca(request):
    if request.method == 'POST':
        form = PCAForm(request.POST, request.FILES)
        itens_formset = ItemPCAFormSet(request.POST, prefix='itens')

        if form.is_valid() and itens_formset.is_valid():
            try:
                with transaction.atomic():
                    pca = form.save(commit=False)
                    pca.responsavel_aprovacao = request.user # Associa o usuário logado
                    pca.save()

                    itens_formset.instance = pca
                    itens_formset.save()

                messages.success(request, 'PCA criado com sucesso!')
                return redirect('contratacoes:detalhar_pca', pk=pca.pk)
            except Exception as e:
                messages.error(request, f"Não foi possível criar o PCA devido a um erro inesperado: {e}")
                print(f"Erro no salvamento do PCA: {e}")
        else:
            messages.error(request, 'Erro ao criar PCA. Verifique os campos.')
            print("Erros do formulário PCA:", form.errors)
            print("Erros do formset de Itens PCA:", itens_formset.errors)
    else:
        form = PCAForm()
        itens_formset = ItemPCAFormSet(prefix='itens')

    context = {
        'form': form,
        'itens_formset': itens_formset,
        'titulo_pagina': 'Criar Novo PCA',
    }
    return render(request, 'contratacoes/criar_pca.html', context)


@login_required
def detalhar_pca(request, pk):
    pca = get_object_or_404(PCA, pk=pk)
    itens_pca = pca.itens.all() # Acessa os itens relacionados
    context = {
        'pca': pca,
        'itens_pca': itens_pca,
        'titulo_pagina': f'Detalhes do PCA {pca.ano_vigencia}',
    }
    return render(request, 'contratacoes/detalhar_pca.html', context)

@login_required
def editar_pca(request, pk):
    pca = get_object_or_404(PCA, pk=pk)

    # Restrição de permissão: Apenas o responsável pela aprovação ou superusuário
    if pca.responsavel_aprovacao != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para editar este PCA.')
        return redirect('contratacoes:detalhar_pca', pk=pca.pk)

    if request.method == 'POST':
        form = PCAForm(request.POST, request.FILES, instance=pca)
        itens_formset = ItemPCAFormSet(request.POST, instance=pca, prefix='itens')

        if form.is_valid() and itens_formset.is_valid():
            try:
                with transaction.atomic():
                    pca = form.save()
                    itens_formset.instance = pca
                    itens_formset.save()
                messages.success(request, 'PCA atualizado com sucesso!')
                return redirect('contratacoes:detalhar_pca', pk=pca.pk)
            except Exception as e:
                messages.error(request, f"Não foi possível atualizar o PCA devido a um erro inesperado: {e}")
                print(f"Erro na atualização do PCA: {e}")
        else:
            messages.error(request, 'Erro ao atualizar PCA. Verifique os campos.')
            print("Erros do formulário PCA (Edição):", form.errors)
            print("Erros do formset de Itens PCA (Edição):", itens_formset.errors)
    else:
        form = PCAForm(instance=pca)
        itens_formset = ItemPCAFormSet(instance=pca, prefix='itens')

    context = {
        'form': form,
        'itens_formset': itens_formset,
        'pca': pca,
        'titulo_pagina': f'Editar PCA {pca.ano_vigencia}',
    }
    return render(request, 'contratacoes/editar_pca.html', context)


# Em SysGov_Project/contratacoes/views.py

from django.contrib.contenttypes.models import ContentType # <<< ADICIONE ESTA IMPORTAÇÃO NO TOPO

# ... (resto das suas importações) ...

@login_required
def adicionar_anexo_etp(request, etp_id):
    etp = get_object_or_404(ETP, pk=etp_id)
    # Verificar permissão... (seu código aqui está correto)
    if etp.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para adicionar anexos a este ETP.')
        return redirect('contratacoes:detalhar_etp', pk=etp.pk)

    if request.method == 'POST':
        form = ArquivoAnexoForm(request.POST, request.FILES)
        if form.is_valid():
            anexo = form.save(commit=False)
            anexo.uploaded_by = request.user
            
            # --- INÍCIO DA CORREÇÃO ---
            # Aqui definimos o "pai" do anexo diretamente nele, antes de salvar.
            anexo.content_type = ContentType.objects.get_for_model(etp) # Diz que o pai é um ETP
            anexo.object_id = etp.pk                                     # Diz qual ETP específico é o pai
            # --- FIM DA CORREÇÃO ---

            anexo.save() # Agora salvamos o anexo, que já sabe quem é seu pai

            # A linha etp.anexos.add(anexo) NÃO é mais necessária e foi removida.
            
            messages.success(request, 'Anexo adicionado ao ETP com sucesso!')
            return redirect('contratacoes:detalhar_etp', pk=etp.pk)
        else:
            messages.error(request, 'Erro ao adicionar anexo. Verifique o formulário.')
    else:
        form = ArquivoAnexoForm()

    context = {
        'form': form,
        'etp': etp,
        'titulo_pagina': f'Adicionar Anexo ao ETP: {etp.titulo}'
    }
    return render(request, 'contratacoes/adicionar_anexo_etp.html', context)

# View para adicionar anexo a um TR
@login_required
def adicionar_anexo_tr(request, tr_id):
    tr = get_object_or_404(TR, pk=tr_id)
    # Verificar permissão: apenas o autor ou superuser pode adicionar anexos
    if tr.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para adicionar anexos a este TR.')
        return redirect('contratacoes:detalhar_tr', pk=tr.pk)

    if request.method == 'POST':
        form = ArquivoAnexoForm(request.POST, request.FILES) # Usa o formulário do core
        if form.is_valid():
            anexo = form.save(commit=False)
            anexo.uploaded_by = request.user
            anexo.save() # Salva o ArquivoAnexo primeiro para ter um PK
            tr.anexos.add(anexo) # Adiciona o anexo ao ManyToManyField do TR
            messages.success(request, 'Anexo adicionado ao TR com sucesso!')
            return redirect('contratacoes:detalhar_tr', pk=tr.pk)
        else:
            messages.error(request, 'Erro ao adicionar anexo. Verifique o formulário.')
    else:
        form = ArquivoAnexoForm()

    context = {
        'form': form,
        'tr': tr,
        'titulo_pagina': f'Adicionar Anexo ao TR: {tr.titulo}'
    }
    return render(request, 'contratacoes/adicionar_anexo.html', context) # Reutilizar template ou criar um específico


# --- Views para Modelos de Texto ---
@login_required
def listar_modelos_texto(request):
    modelos = ModeloTexto.objects.all().order_by('titulo')
    context = {
        'modelos': modelos,
        'titulo_pagina': 'Modelos de Texto',
    }
    return render(request, 'contratacoes/listar_modelos_texto.html', context)

# --- Views para Requisitos Padrão ---
@login_required
def listar_requisitos_padrao(request):
    requisitos = RequisitoPadrao.objects.all().order_by('codigo')
    context = {
        'requisitos': requisitos,
        'titulo_pagina': 'Requisitos Padrão',
    }
    return render(request, 'contratacoes/listar_requisitos_padrao.html', context)



@login_required
def contratacoes_dashboard(request):
    total_etps = ETP.objects.count()
    etps_em_elaboracao = ETP.objects.filter(status='EM_ELABORACAO') # This already passes the queryset
    etps_aprovados_list = ETP.objects.filter(status='APROVADO') # <<< NEW: Pass the queryset for approved ETPs
    total_trs = TR.objects.count()
    trs_aprovados = TR.objects.filter(status='APROVADO').count()
    total_pcas = PCA.objects.count()
    # Add more metrics as needed

    context = {
        'total_etps': total_etps,
        'etps_em_elaboracao': etps_em_elaboracao,
        'total_em_elaboracao': etps_em_elaboracao.count(), # Pass count for title if needed
        'etps_aprovados': etps_aprovados_list, # <<< NEW: Pass the queryset to the template
        'total_aprovados': etps_aprovados_list.count(), # <<< NEW: Pass the count for the title
        'total_trs': total_trs,
        'trs_aprovados': trs_aprovados,
        'total_pcas': total_pcas,
        'titulo_pagina': 'Dashboard de Contratações',
    }
    return render(request, 'contratacoes/dashboard.html', context)



@login_required 
def gerar_etp_pdf(request, pk):
    etp = get_object_or_404(ETP, pk=pk)

    # Calculando a média dos preços (se necessário para o PDF)
    media_precos = etp.pesquisas_preco.aggregate(Avg('valor_cotado'))['valor_cotado__avg'] or 0

    context = {
        'etp': etp,
        'media_precos': media_precos,
    }
 
    html_string = render_to_string('contratacoes/etp_pdf_template.html', context)

    # Converte o HTML para PDF usando WeasyPrint
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf()

    # Cria uma resposta HTTP com o PDF para download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ETP_{etp.pk}.pdf"'
    return response



# Em contratacoes/views.py

@login_required
def gerar_tr_pdf(request, pk):
    """
    Gera o documento oficial do Termo de Referência em formato PDF.
    """
    try:
        tr = get_object_or_404(TR, pk=pk)
        
        context = {
            'tr': tr
        }

        # Renderiza o nosso template HTML final e completo
        html_string = render_to_string('contratacoes/tr_pdf.html', context)
        
        # Converte a string HTML para PDF
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        
        # Cria a resposta HTTP para o navegador
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="TR_{tr.numero_processo}.pdf"'
        
        return response

    except Exception as e:
        # Se algo der errado, mostra uma mensagem de erro e volta para a página de detalhes
        messages.error(request, f"Ocorreu um erro ao gerar o PDF: {e}")
        return redirect('contratacoes:detalhar_tr', pk=pk)
@login_required
@permission_required('contratacoes.add_tr', raise_exception=True)
def gerar_tr_a_partir_etp(request, pk):
    etp = get_object_or_404(ETP, pk=pk)
    if etp.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para gerar um TR a partir deste ETP.')
        return redirect('contratacoes:detalhar_etp', pk=etp.pk)

    if etp.status != 'APROVADO':
        if not request.user.is_superuser:
            messages.warning(request, f"Não é possível gerar o TR: o ETP '{etp.titulo}' ainda não está APROVADO.")
            return redirect('contratacoes:detalhar_etp', pk=etp.pk)
        else:
            messages.info(request, f"O ETP '{etp.titulo}' não está APROVADO, mas você é superusuário. Prossiga para teste.")

    if hasattr(etp, 'termo_referencia'):
        messages.info(request, "Este ETP já possui um TR vinculado. Você será redirecionado para editá-lo.")
        return redirect('contratacoes:detalhar_tr', pk=etp.termo_referencia.pk)

    if request.method == 'POST':
        form = TRForm(request.POST, etp_origem=etp)
        if form.is_valid():
            tr = form.save(commit=False)
            tr.etp_origem = etp
            if etp.processo_vinculado:
                tr.processo_vinculado = etp.processo_vinculado
            tr.elaborador = request.user
            tr.save()
            messages.success(request, 'Termo de Referência gerado com sucesso!')
            if tr.processo_vinculado:
                return redirect('detalhes_processo', processo_id=tr.processo_vinculado.id)
            else:
                return redirect('contratacoes:detalhar_tr', pk=tr.pk)
        else:
            messages.error(request, 'Erro ao gerar Termo de Referência. Verifique os campos.')
            print("====================================")
            print("ERRO DE VALIDAÇÃO DO FORMULÁRIO TR:")
            print("Erros do formulário principal (TR):", form.errors)
            print("Erros não-campo do formulário principal (TR):", form.non_field_errors)
            print("====================================")
    else:
        initial_data = {
            'objeto': etp.objetivo_contratacao,
            'justificativa': etp.descricao_necessidade,
            'especificacoes_tecnicas': etp.requisitos_contratacao,
            'estimativa_preco_tr': etp.estimativa_valor,
        }
        form = TRForm(initial=initial_data, etp_origem=etp)
    context = {
        'etp': etp,
        'form': form,
        'titulo_pagina': f'Gerar TR a partir do ETP: {etp.titulo}'
    }
    return render(request, 'contratacoes/gerar_tr_a_partir_etp.html', context)

# SysGov_Project/contratacoes/views.py
# ... (outras importações) ...

@login_required
def gerar_etp_ia_view(request):
    rascunho_gerado = None
    if request.method == 'POST':
        descricao = request.POST.get('descricao_necessidade')
        if descricao:
            rascunho_gerado = ai_services.gerar_rascunho_etp_com_ia(descricao)
            if "Ocorreu um erro" not in rascunho_gerado:
                # <<< NOVA LÓGICA AQUI >>>
                # Usamos o parser para extrair os dados
                dados_etp_parseados = ai_services.parse_rascunho_etp(rascunho_gerado)
                # Salvamos os dados na sessão para usar na próxima página
                request.session['dados_etp_ia'] = dados_etp_parseados

    context = {
        'rascunho_gerado': rascunho_gerado
    }
    return render(request, 'contratacoes/gerar_etp_ia.html', context)

# Substitua a função existente por esta
def parse_rascunho_etp(rascunho_texto):
    """
    Versão Final: Lê o rascunho completo da IA e mapeia para os campos do modelo.
    """
    dados_etp = {}
    padrao = r"\*\*(?:\d+\.\s*)?([^:]+):\*\*\s*(.*?)(?=\n\*\*\s*[\d\w]|\Z)"
    partes = re.findall(padrao, rascunho_texto, re.DOTALL)

    mapa_campos = {
        'TÍTULO SUGERIDO': 'titulo',
        'SETOR DEMANDANTE SUGERIDO': 'setor_demandante',
        'DESCRIÇÃO DA NECESSIDADE': 'descricao_necessidade',
        'OBJETIVO DA CONTRATAÇÃO': 'objetivo_contratacao',
        'REQUISITOS DA CONTRATAÇÃO': 'requisitos_contratacao',
        'LEVANTAMENTO DE SOLUÇÕES DE MERCADO': 'levantamento_solucoes_mercado',
        'ESTIMATIVA DAS QUANTIDADES': 'estimativa_quantidades',
        'ESTIMATIVA DO VALOR DA CONTRATAÇÃO (R$)': 'resultados_esperados',
        'RESULTADOS ESPERADOS': 'resultados_esperados',
        'VIABILIDADE E JUSTIFICATIVA DA SOLUÇÃO ESCOLHIDA': 'viabilidade_justificativa_solucao',
        'ALINHAMENTO COM O PLANEJAMENTO ESTRATÉGICO': 'alinhamento_planejamento', # <<< CAMPO NOVO ADICIONADO
    }

    for titulo, conteudo in partes:
        titulo_limpo = titulo.strip().upper()
        if titulo_limpo in mapa_campos:
            campo_modelo = mapa_campos[titulo_limpo]
            if campo_modelo not in dados_etp:
                dados_etp[campo_modelo] = conteudo.strip()

    return dados_etp

# Em SysGov_Project/contratacoes/views.py

@login_required
def processar_acao_etp(request, pk):
    etp = get_object_or_404(ETP, pk=pk)
    acao = request.POST.get('acao')

    # Ação: Submeter para análise
    if acao == 'submeter_analise' and etp.status == 'EM_ELABORACAO':
        if request.user.has_perm('contratacoes.pode_submeter_etp_analise'):
            etp.status = 'AGUARDANDO_ANALISE'
            etp.save()
            messages.success(request, 'ETP submetido para Análise de Requerimentos.')
        else:
            messages.error(request, 'Você não tem permissão para submeter este ETP.')

    # Ações da Análise de Requerimentos
    elif acao == 'aprovar_analise' and etp.status == 'AGUARDANDO_ANALISE':
        if request.user.has_perm('contratacoes.pode_aprovar_etp_analise'):
            etp.status = 'AGUARDANDO_ORCAMENTO'
            etp.save()
            messages.success(request, 'ETP aprovado pela Análise. Enviado para o Setor de Orçamento.')
        else:
            messages.error(request, 'Você não tem permissão para aprovar este ETP.')
    
    elif acao == 'recusar_analise' and etp.status == 'AGUARDANDO_ANALISE':
        if request.user.has_perm('contratacoes.pode_recusar_etp_analise'):
            etp.status = 'RECUSADO_ANALISE'
            etp.save()
            messages.warning(request, 'ETP foi recusado pela Análise e devolvido para elaboração.')
        else:
            messages.error(request, 'Você não tem permissão para recusar este ETP.')

    # --- INÍCIO DA NOVA LÓGICA ADICIONADA ---
    # Ações do Setor de Orçamento
    elif acao == 'aprovar_orcamento' and etp.status == 'AGUARDANDO_ORCAMENTO':
        if request.user.has_perm('contratacoes.pode_aprovar_etp_orcamento'):
            etp.status = 'APROVADO' # Estado final do ETP!
            etp.save()
            messages.success(request, 'ETP aprovado pelo Orçamento! O processo pode continuar.')
        else:
            messages.error(request, 'Você não tem permissão para aprovar o orçamento deste ETP.')
            
    elif acao == 'recusar_orcamento' and etp.status == 'AGUARDANDO_ORCAMENTO':
        if request.user.has_perm('contratacoes.pode_recusar_etp_orcamento'):
            etp.status = 'RECUSADO_ORCAMENTO'
            etp.save()
            messages.warning(request, 'ETP foi recusado pelo Setor de Orçamento.')
        else:
            messages.error(request, 'Você não tem permissão para recusar o orçamento deste ETP.')
    # --- FIM DA NOVA LÓGICA ADICIONADA ---

    else:
        messages.warning(request, 'Ação inválida ou não permitida para o status atual do ETP.')

    return redirect('contratacoes:detalhar_etp', pk=etp.pk) 

# Em SysGov_Project/contratacoes/views.py

# ... (outras importações e views) ...

@login_required
def editar_item_catalogo(request, pk):
    item = get_object_or_404(ItemCatalogo, pk=pk)
    
    if request.method == 'POST':
        form = ItemCatalogoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item do Catálogo atualizado com sucesso!')
            return redirect('contratacoes:listar_catalogo_itens')
        else:
            messages.error(request, 'Erro ao atualizar o item. Verifique o formulário.')
    else: # Se a requisição for GET
        form = ItemCatalogoForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'titulo_pagina': f'Editar Item: {item.nome_padronizado}',
    }
    return render(request, 'contratacoes/editar_item_catalogo.html', context)

# Em contratacoes/views.py

from .forms import ContratoForm # Adicione ContratoForm na sua lista de importações de forms
from core.models import Processo # Adicione a importação do Processo

# ... (outras views) ...

@login_required
def criar_contrato(request, processo_id):
    processo = get_object_or_404(Processo, pk=processo_id)
    
    if request.method == 'POST':
        form = ContratoForm(request.POST)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.processo_vinculado = processo # Vincula ao processo da URL
            contrato.save()
            messages.success(request, f"Contrato {contrato.numero_contrato}/{contrato.ano_contrato} criado com sucesso!")
            return redirect('detalhes_processo', processo_id=processo.pk) # Volta para a página do processo
    else:
        form = ContratoForm()
        
    context = {
        'form': form,
        'processo': processo,
        'titulo_pagina': f'Adicionar Contrato ao Processo {processo.numero_protocolo}'
    }
    return render(request, 'contratacoes/criar_contrato.html', context)

# Em contratacoes/views.py

@login_required
def listar_contratos(request):
    # Por enquanto, vamos listar todos. No futuro, podemos adicionar filtros por usuário.
    contratos = Contrato.objects.all().order_by('-data_assinatura')
    
    context = {
        'contratos': contratos,
        'titulo_pagina': 'Gestão de Contratos'
    }
    return render(request, 'contratacoes/listar_contratos.html', context)

# Em contratacoes/views.py

@login_required
def detalhar_contrato(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    # Buscamos os empenhos já vinculados a este contrato
    notas_empenho = contrato.notas_empenho.all()

    context = {
        'contrato': contrato,
        'notas_empenho': notas_empenho,
        'titulo_pagina': f'Detalhes do Contrato {contrato.numero_contrato}/{contrato.ano_contrato}'
    }
    return render(request, 'contratacoes/detalhar_contrato.html', context)

# Em contratacoes/views.py

@login_required
def editar_contrato(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    
    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrato atualizado com sucesso!')
            return redirect('contratacoes:detalhar_contrato', pk=contrato.pk)
    else:
        form = ContratoForm(instance=contrato)
        
    context = {
        'form': form,
        'contrato': contrato,
        'titulo_pagina': f'Editar Contrato {contrato.numero_contrato}/{contrato.ano_contrato}'
    }
    return render(request, 'contratacoes/editar_contrato.html', context)



@login_required
def assistente_tr_ia_view(request, etp_pk):
    """
    Pega um ETP aprovado, envia para a IA e mostra o rascunho do TR.
    """
    etp = get_object_or_404(ETP, pk=etp_pk, status='APROVADO')
    
    # Montamos um texto único com todas as informações do ETP para dar contexto à IA
    texto_etp_completo = f"""
    Título do ETP: {etp.titulo}
    Número do Processo: {etp.numero_processo}
    Setor Demandante: {etp.setor_demandante}
    Descrição da Necessidade: {etp.descricao_necessidade}
    Objetivo da Contratação: {etp.objetivo_contratacao}
    Requisitos da Contratação: {etp.requisitos_contratacao}
    Estimativa de Quantidades: {etp.estimativa_quantidades}
    Estimativa de Valor: R$ {etp.estimativa_valor}
    Resultados Esperados: {etp.resultados_esperados}
    Justificativa da Solução: {etp.viabilidade_justificativa_solucao}
    Alinhamento Estratégico: {etp.alinhamento_planejamento}
    """
    
    rascunho_tr_gerado = ai_services.gerar_rascunho_tr_com_ia(texto_etp_completo)

    context = {
        'etp': etp,
        'rascunho_gerado': rascunho_tr_gerado,
        'titulo_pagina': 'Assistente de IA para Termo de Referência'
    }
    
    return render(request, 'contratacoes/gerar_tr_ia.html', context)

# Adicione esta view ao seu contratacoes/views.py

@login_required
def gerar_contrato_pdf(request, pk):
    """
    Gera o documento oficial do Contrato em formato PDF.
    """
    try:
        contrato = get_object_or_404(Contrato, pk=pk)
        
        context = {
            'contrato': contrato
        }

        # 1. Renderiza o nosso template HTML para uma string
        html_string = render_to_string('contratacoes/contrato_pdf.html', context)
        
        # 2. Converte a string HTML para PDF
        pdf_file = HTML(string=html_string).write_pdf()
        
        # 3. Cria a resposta HTTP para o navegador
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="contrato_{contrato.numero_contrato}_{contrato.ano_contrato}.pdf"'
        
        return response

    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao gerar o PDF: {e}")
        return redirect('contratacoes:detalhar_contrato', pk=pk)


@login_required
def listar_atas_rp(request):
    atas = AtaRegistroPrecos.objects.all().order_by('-data_assinatura')
    context = {
        'atas': atas,
        'titulo_pagina': 'Atas de Registro de Preços'
    }
    return render(request, 'contratacoes/listar_atas_rp.html', context)


@login_required
def detalhar_ata_rp(request, pk):
    ata = get_object_or_404(AtaRegistroPrecos, pk=pk)
    context = {
        'ata': ata,
        'titulo_pagina': f'Detalhes da Ata de RP {ata.numero_ata}/{ata.ano_ata}'
    }
    return render(request, 'contratacoes/detalhar_ata_rp.html', context)
