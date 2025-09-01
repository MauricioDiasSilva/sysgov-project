# SysGov_Project/contratacoes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Count, Q, F # Manter Q se for usar para queries mais complexas
from django.forms import inlineformset_factory
from django.template.loader import render_to_string
# from weasyprint import HTML, CSS # Descomente se for usar para gerar PDFs
import json
# from django.contrib.auth.models import User # Geralmente não necessário se usar settings.AUTH_USER_MODEL
# from django.conf import settings # Geralmente não necessário diretamente em views, apenas em models ou settings
from decimal import Decimal # Necessário para cálculos com DecimalField
from . import ai_services
# Importação crucial do modelo Processo e ArquivoAnexo do app 'core'
from core.models import Processo, ArquivoAnexo # <<< Importação corrigida para ArquivoAnexo
from django.forms import inlineformset_factory
# Importar os modelos da sua própria app 'contratacoes'
from .models import (
    ETP, TR, PCA, ItemPCA, PesquisaPreco, ParecerTecnico,
    ModeloTexto, RequisitoPadrao, ItemCatalogo, STATUS_DOCUMENTO_CHOICES
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

@login_required 
def listar_etps(request):
    # Lógica de Permissão interna
    if not request.user.has_perm('contratacoes.view_etp') and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para visualizar esta lista de ETPs.")
        return redirect('home') # Redireciona para a página inicial com a mensagem

    # Lê o parâmetro 'status' da URL. Se não existir, a variável é None.
    status_filtro = request.GET.get('status') 

    # Inicia com todos os ETPs
    etps = ETP.objects.all()

    # Se um status foi passado na URL, filtra o queryset
    if status_filtro:
        etps = etps.filter(status=status_filtro)
    
    # Ordena os resultados
    etps = etps.order_by('-data_criacao')

    context = {
        'etps': etps,
        'titulo_pagina': 'Lista de ETPs',
        'status_filtro': status_filtro, # Passa o status do filtro para o template
    }
    return render(request, 'contratacoes/listar_etps.html', context)

# Em SysGov_Project/contratacoes/views.py

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
        print("--- DENTRO DO POST ---") # ESPIÃO 1
        form = ETPForm(request.POST)
        pesquisas_formset = PesquisaPrecoFormSet(request.POST, prefix='pesquisas')
        pareceres_formset = ParecerTecnicoFormSet(request.POST, prefix='pareceres')

        # Vamos verificar a validade de cada um separadamente
        form_valido = form.is_valid()
        pesquisas_valido = pesquisas_formset.is_valid()
        pareceres_valido = pareceres_formset.is_valid()

        print(f"Formulário principal é válido? {form_valido}") # ESPIÃO 2
        print(f"Formset de Pesquisas é válido? {pesquisas_valido}") # ESPIÃO 3
        print(f"Formset de Pareceres é válido? {pareceres_valido}") # ESPIÃO 4

        if not pesquisas_valido:
            print("--- ERROS NO FORMSET DE PESQUISAS ---") # ESPIÃO 5
            print(pesquisas_formset.errors)
            print(pesquisas_formset.non_form_errors())


        if form_valido and pesquisas_valido and pareceres_valido:
            print("--- TUDO VÁLIDO, TENTANDO SALVAR ---") # ESPIÃO 6
            try:
                with transaction.atomic():
                    etp = form.save(commit=False)
                    etp.autor = request.user
                    if processo_core:
                        etp.processo_vinculado = processo_core
                    etp.save()
                    print("--- ETP PRINCIPAL SALVO COM SUCESSO ---") # ESPIÃO 7

                    pesquisas_formset.instance = etp
                    pesquisas_formset.save()
                    print("--- FORMSET DE PESQUISAS SALVO COM SUCESSO ---") # ESPIÃO 8

                    pareceres_formset.instance = etp
                    pareceres_formset.save()

                    messages.success(request, 'ETP criado com sucesso!')
                    if processo_core:
                        return redirect('detalhes_processo', processo_id=processo_core.id)
                    else:
                        return redirect('contratacoes:detalhar_etp', pk=etp.pk)
            except Exception as e:
                messages.error(request, f"Ocorreu um erro inesperado: {e}")

        else:
            messages.error(request, 'Erro de validação. Verifique os campos.')

    else:  # GET request
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

@login_required
def editar_etp(request, pk):
    etp = get_object_or_404(ETP, pk=pk)

    # Lógica de permissão e status:
    # Apenas o autor ou um superusuário pode editar
    if etp.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para editar este ETP.')
        return redirect('contratacoes:detalhar_etp', pk=etp.pk)

    # Restrição de edição baseada no status (ex: não edita se já aprovado/recusado/cancelado)
    if etp.status in ['APROVADO', 'RECUSADO', 'CANCELADO'] and not request.user.is_superuser:
        messages.warning(request, f'Este ETP está em status "{etp.get_status_display()}". Edições não são permitidas.')
        return redirect('contratacoes:detalhar_etp', pk=etp.pk)

    if request.method == 'POST':
        form = ETPForm(request.POST, instance=etp)
        pesquisas_formset = PesquisaPrecoFormSet(request.POST, instance=etp, prefix='pesquisas')
        pareceres_formset = ParecerTecnicoFormSet(request.POST, instance=etp, prefix='pareceres')

        if form.is_valid() and pesquisas_formset.is_valid() and pareceres_formset.is_valid():
            try:
                with transaction.atomic():
                    etp = form.save(commit=False)
                    # A data_ultima_atualizacao é auto_now=True no modelo
                    etp.save()

                    pesquisas_formset.instance = etp
                    pesquisas_formset.save()

                    pareceres_formset.instance = etp
                    pareceres_formset.save()

                messages.success(request, 'ETP atualizado com sucesso!')
                return redirect('contratacoes:detalhar_etp', pk=etp.pk)
            except Exception as e:
                messages.error(request, f"Não foi possível atualizar o ETP devido a um erro inesperado: {e}")
                print(f"Erro na atualização do ETP (bloco try/except): {e}")
        else:
            messages.error(request, 'Erro ao atualizar ETP. Verifique os campos.')
            print("====================================")
            print("ERRO DE VALIDAÇÃO DO FORMULÁRIO ETP (EDIÇÃO):")
            print("Erros do formulário principal (ETP):", form.errors)
            print("Erros não-campo do formulário principal (ETP):", form.non_field_errors)
            print("Erros do formset de Pesquisas:", pesquisas_formset.errors)
            print("Erros do formset de Pareceres:", pareceres_formset.errors)
            print("====================================")
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

# --- VIEWS PARA TR ---
@login_required
def listar_trs(request):
    trs = TR.objects.filter(autor=request.user).order_by('-data_criacao')
    context = {
        'trs': trs,
        'titulo_pagina': 'Meus Termos de Referência',
    }
    return render(request, 'contratacoes/listar_trs.html', context)

@login_required
def criar_tr(request, etp_id=None, processo_id=None):
    etp_origem = None
    processo_core = None

    if etp_id:
        etp_origem = get_object_or_404(ETP, id=etp_id)
        # Se já existe um TR para este ETP, redirecione para edição
        if hasattr(etp_origem, 'termo_referencia'):
            messages.info(request, "Este ETP já possui um TR. Você será redirecionado para editá-lo.")
            return redirect('contratacoes:editar_tr', pk=etp_origem.termo_referencia.pk)
        # Se um ETP é fornecido, use o processo vinculado a ele
        if etp_origem.processo_vinculado:
            processo_core = etp_origem.processo_vinculado
    elif processo_id: # Permite criar TR diretamente a partir de um processo, sem ETP
        processo_core = get_object_or_404(Processo, id=processo_id)
        # Opcional: Se já existe um TR vinculado a este Processo, redirecione para editá-lo
        if hasattr(processo_core, 'tr_documento'):
            messages.info(request, "Este processo já possui um TR. Você será redirecionado para editá-lo.")
            return redirect('contratacoes:editar_tr', pk=processo_core.tr_documento.pk)


    if request.method == 'POST':
        form = TRForm(request.POST)
        if form.is_valid():
            tr = form.save(commit=False)
            tr.autor = request.user
            if etp_origem:
                tr.etp_origem = etp_origem
            if processo_core:
                tr.processo_vinculado = processo_core # Vincula ao processo
            tr.save()
            messages.success(request, 'Termo de Referência criado com sucesso!')
            if processo_core:
                return redirect('detalhes_processo', processo_id=processo_core.id)
            elif etp_origem:
                return redirect('contratacoes:detalhar_etp', pk=etp_origem.pk)
            else:
                return redirect('contratacoes:detalhar_tr', pk=tr.pk)
        else:
            messages.error(request, 'Erro ao criar Termo de Referência. Verifique os campos.')
    else: # GET request
        initial_data = {}
        if etp_origem:
            initial_data['titulo'] = f"TR do ETP: {etp_origem.titulo}"
            initial_data['numero_processo'] = etp_origem.numero_processo # Preenche com o número do processo do ETP
            initial_data['justificativa'] = etp_origem.descricao_necessidade # Sugestão de cópia
            initial_data['objeto'] = etp_origem.objetivo_contratacao # Sugestão de cópia
            initial_data['estimativa_preco_tr'] = etp_origem.estimativa_valor # Sugestão de cópia
        elif processo_core:
             initial_data['numero_processo'] = processo_core.numero_protocolo
             initial_data['titulo'] = f"TR para processo: {processo_core.titulo}"


        form = TRForm(initial=initial_data)

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


# --- VIEWS PARA ANEXOS (com base em core.ArquivoAnexo) ---
# View para adicionar anexo a um ETP
@login_required
def adicionar_anexo_etp(request, etp_id):
    etp = get_object_or_404(ETP, pk=etp_id)
    # Verificar permissão: apenas o autor ou superuser pode adicionar anexos
    if etp.autor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para adicionar anexos a este ETP.')
        return redirect('contratacoes:detalhar_etp', pk=etp.pk)

    if request.method == 'POST':
        form = ArquivoAnexoForm(request.POST, request.FILES) # Usa o formulário do core
        if form.is_valid():
            anexo = form.save(commit=False)
            anexo.uploaded_by = request.user
            anexo.save() # Salva o ArquivoAnexo primeiro para ter um PK
            etp.anexos.add(anexo) # Adiciona o anexo ao ManyToManyField do ETP
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
    return render(request, 'contratacoes/adicionar_anexo.html', context) # Reutilizar template ou criar um específico

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



def gerar_tr_pdf(request, pk):
    tr = get_object_or_404(TR, pk=pk)

    context = {
        'tr': tr,
    }

    html_string = render_to_string('contratacoes/tr_pdf_template.html', context)

    # Converte o HTML para PDF usando WeasyPrint
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf()

    # Cria uma resposta HTTP com o PDF para download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="TR_{tr.pk}.pdf"'
    return response

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