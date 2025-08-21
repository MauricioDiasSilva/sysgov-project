# SysGov_Project/integracao_audesp/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
import json
from decimal import Decimal
import datetime
from django.contrib import messages
from django.shortcuts import redirect
from .forms import AudespAjusteContratualForm
# Importe os modelos necessários de outros apps
from contratacoes.models import ETP, TR
# EditalPublicacao foi removido de licitacoes.models, então não o importamos daqui.
from licitacoes.models import Edital, Lote, ItemLicitado
from financeiro.models import DocumentoFiscal, Pagamento

# Importe todos os modelos do próprio app 'integracao_audesp'
from .models import (
    AudespConfiguracao,
    SubmissaoAudesp,
    AudespAjusteContratual,
    AudespAtaRegistroPrecos,
    AudespEmpenhoContrato,
    AudespEditalDetalhado
)
from django.contrib.contenttypes.models import ContentType



@login_required
def criar_ajuste_contratual_audesp(request, processo_id=None, resultado_id=None):
    processo_ref = None
    resultado_ref = None

    if processo_id:
        processo_ref = get_object_or_404(Processo, pk=processo_id)
    if resultado_id:
        resultado_ref = get_object_or_404(ResultadoLicitacao, pk=resultado_id)

    if request.method == 'POST':
        form = AudespAjusteContratualForm(request.POST)
        if form.is_valid():
            ajuste = form.save(commit=False)
            ajuste.criado_por = request.user
            # Vincula aos objetos de referência se fornecidos
            if processo_ref:
                ajuste.processo_vinculado = processo_ref
            if resultado_ref:
                ajuste.resultado_licitacao_origem = resultado_ref
                ajuste.edital_origem = resultado_ref.edital # Tenta vincular o Edital do Resultado
            ajuste.save()
            messages.success(request, 'Ajuste Contratual AUDESP criado com sucesso!')
            return redirect('integracao_audesp:detalhar_ajuste_contratual_audesp', pk=ajuste.pk)
        else:
            messages.error(request, 'Erro ao criar Ajuste Contratual. Verifique o formulário.')
    else: # GET request
        initial_data = {}
        if processo_ref:
            initial_data['processo_sistema_origem'] = processo_ref.numero_protocolo
            # Tente preencher outros campos com base no processo/resultado/edital
            # Ex: initial_data['ano_contrato'] = processo_ref.data_criacao.year
        if resultado_ref:
            initial_data['ni_fornecedor'] = resultado_ref.cnpj_vencedor
            initial_data['nome_razao_social_fornecedor'] = resultado_ref.fornecedor_vencedor
            initial_data['valor_inicial'] = resultado_ref.valor_homologado
            initial_data['valor_global'] = resultado_ref.valor_homologado
            # Tentar preencher codigo_edital_audesp do edital do resultado
            if resultado_ref.edital:
                initial_data['codigo_edital_audesp'] = resultado_ref.edital.numero_edital

        form = AudespAjusteContratualForm(initial=initial_data)
        # Para popular o queryset de ForeignKeys do form:
        form.fields['processo_vinculado'].queryset = Processo.objects.all().order_by('numero_protocolo')
        form.fields['resultado_licitacao_origem'].queryset = ResultadoLicitacao.objects.all().order_by('-data_homologacao')
        form.fields['edital_origem'].queryset = Edital.objects.all().order_by('-data_publicacao')

        # Se for editar, o criado_por já estaria na instância, mas para criar, preenchemos na view
        if request.user.is_authenticated:
            form.fields['criado_por'].initial = request.user.pk
            # Desabilita o campo 'criado_por' se você não quer que o usuário o altere
            form.fields['criado_por'].widget.attrs['disabled'] = 'disabled'
            form.fields['criado_por'].widget.attrs['class'] = 'form-control-plaintext' # Estilo para campo desabilitado

    context = {
        'form': form,
        'titulo_pagina': 'Criar Novo Ajuste Contratual AUDESP',
        'processo_ref': processo_ref,
        'resultado_ref': resultado_ref,
    }
    return render(request, 'integracao_audesp/criar_ajuste_contratual_audesp.html', context)

@login_required
def editar_ajuste_contratual_audesp(request, pk):
    ajuste = get_object_or_404(AudespAjusteContratual, pk=pk)

    # Opcional: Lógica de permissão (apenas o criador ou admin pode editar)
    if ajuste.criado_por != request.user and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para editar este Ajuste Contratual AUDESP.")
        return redirect('integracao_audesp:detalhar_ajuste_contratual_audesp', pk=ajuste.pk)

    if request.method == 'POST':
        form = AudespAjusteContratualForm(request.POST, instance=ajuste)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ajuste Contratual AUDESP atualizado com sucesso!')
            return redirect('integracao_audesp:detalhar_ajuste_contratual_audesp', pk=ajuste.pk)
        else:
            messages.error(request, 'Erro ao atualizar Ajuste Contratual. Verifique o formulário.')
    else: # GET request
        form = AudespAjusteContratualForm(instance=ajuste)
        # Para popular o queryset de ForeignKeys do form:
        form.fields['processo_vinculado'].queryset = Processo.objects.all().order_by('numero_protocolo')
        form.fields['resultado_licitacao_origem'].queryset = ResultadoLicitacao.objects.all().order_by('-data_homologacao')
        form.fields['edital_origem'].queryset = Edital.objects.all().order_by('-data_publicacao')
        # Desabilita o campo 'criado_por' na edição também
        form.fields['criado_por'].widget.attrs['disabled'] = 'disabled'
        form.fields['criado_por'].widget.attrs['class'] = 'form-control-plaintext'

    context = {
        'form': form,
        'ajuste': ajuste,
        'titulo_pagina': f'Editar Ajuste Contratual AUDESP: {ajuste.codigo_contrato_audesp}',
    }
    return render(request, 'integracao_audesp/editar_ajuste_contratual_audesp.html', context)

# ... (suas views de geração de JSON existentes: gerar_ajuste_contratual_audesp_json, gerar_ata_rp_audesp_json, gerar_empenho_audesp_json)
# ... (suas views de listagem de submissões AUDESP)


def get_audesp_config_data():
    """Retorna os códigos de município e entidade da configuração AUDESP."""
    try:
        config = AudespConfiguracao.objects.first()
        if config:
            return {
                "municipio_codigo": config.municipio_codigo_audesp,
                "entidade_codigo": config.entidade_codigo_audesp
            }
        else:
            return {"municipio_codigo": 0, "entidade_codigo": 0}
    except AudespConfiguracao.DoesNotExist:
        return {"municipio_codigo": 0, "entidade_codigo": 0}


# --- VIEWS DE GERAÇÃO DE JSON PARA AUDESP (APIs) ---

@login_required
def gerar_etp_audesp_json(request, etp_id):
    etp = get_object_or_404(ETP, pk=etp_id)
    config_data = get_audesp_config_data()

    dados_etp_audesp = {
        "dataGeracao": datetime.date.today().strftime("%Y-%m-%d"),
        "identificadorSoftware": "SysGov",
        "versaoSoftware": "1.0",
        "municipioCodigo": config_data["municipio_codigo"],
        "entidadeCodigo": config_data["entidade_codigo"],

        "identificadorDocumento": etp.numero_processo,
        "tipoDocumento": "ETP",
        "dataCriacao": etp.data_criacao.strftime("%Y-%m-%d"),
        "titulo": etp.titulo,
        "setorDemandante": etp.setor_demandante,
        "valorEstimado": float(etp.estimativa_valor) if etp.estimativa_valor is not None else 0.0,
        "status": etp.status,
        "pesquisasPreco": [
            {
                "fornecedor": p.fornecedor,
                "valorCotado": float(p.valor_cotado),
                "dataPesquisa": p.data_pesquisa.strftime("%Y-%m-%d")
            } for p in etp.pesquisas_preco.all()
        ]
    }
    dados_etp_audesp_limpo = {k: v for k, v in dados_etp_audesp.items() if v is not None and v != '' and (not isinstance(v, list) or len(v) > 0)}
    return JsonResponse(dados_etp_audesp_limpo, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})


@login_required
def gerar_edital_audesp_json(request, edital_id):
    edital = get_object_or_404(Edital, pk=edital_id)
    config_data = get_audesp_config_data()

    descritor_json = {
        "municipio": config_data["municipio_codigo"],
        "entidade": config_data["entidade_codigo"],
        "codigoEdital": edital.numero_edital,
        "retificacao": edital.retificacao,
        "adesaoParticipacao": False,
    }
    descritor_json_limpo = {k: v for k, v in descritor_json.items() if v is not None and v != '' and (not isinstance(v, list) or len(v) > 0)}


    publicacoes_audesp_json = []
    # A EditalPublicacao foi removida de licitacoes.models.
    # Publicações detalhadas serão tratadas via AudespEditalDetalhado no futuro, se necessário.
    # Por ora, garantimos que o JSON não tente acessar uma relação inexistente.
    # Se edital.publicacoes_audesp existia e era uma relação, pode ter sido removida.
    # Se for um JSONField no Edital, ele seria acessado diretamente.
    # Por simplicidade, vamos assumir que não há publicações complexas aqui por enquanto.
    # Se você tiver um campo JSONField em Edital para publicações, use-o aqui.
    # Ex: if edital.publicacoes_json_field: publicacoes_audesp_json = edital.publicacoes_json_field

    itens_licitacao_audesp_json = []
    if hasattr(edital, 'itens_diretos') and edital.itens_diretos.exists():
        for item in edital.itens_diretos.all():
            itens_licitacao_audesp_json.append({
                "numeroItem": item.numero_item_audesp,
                "descricaoItem": item.descricao_item,
                "quantidade": float(item.quantidade),
                "unidadeMedida": item.unidade_medida,
                "materialOuServico": item.material_ou_servico,
                "tipoBeneficio": item.tipo_beneficio,
                "incentivoProdutivoBasico": item.incentivo_produtivo_basico,
                "orcamentoSigiloso": item.orcamento_sigiloso,
                "valorUnitarioEstimado": float(item.valor_unitario_estimado_audesp) if item.valor_unitario_estimado_audesp is not None else None,
                "valorTotal": float(item.valor_total_audesp) if item.valor_total_audesp is not None else None,
                "criterioJulgamento": item.criterio_julgamento,
                "itemCategoria": item.item_categoria,
                "patrimonio": item.patrimonio,
                "codigoRegistroImobiliario": item.codigo_registro_imobiliario,
            })

    lotes_licitacao_audesp_json = []
    if hasattr(edital, 'lotes') and edital.lotes.exists():
        for lote in edital.lotes.all():
            itens_do_lote_json = []
            if hasattr(lote, 'itens') and lote.itens.exists():
                for item in lote.itens.all():
                    itens_do_lote_json.append({
                        "numeroItem": item.numero_item_audesp,
                        "descricaoItem": item.descricao_item,
                        "quantidade": float(item.quantidade),
                        "unidadeMedida": item.unidade_medida,
                        "materialOuServico": item.material_ou_servico,
                        "tipoBeneficio": item.tipo_beneficio,
                        "incentivoProdutivoBasico": item.incentivo_produtivo_basico,
                        "orcamentoSigiloso": item.orcamento_sigiloso,
                        "valorUnitarioEstimado": float(item.valor_unitario_estimado_audesp) if item.valor_unitario_estimado_audesp is not None else None,
                        "valorTotal": float(item.valor_total_audesp) if item.valor_total_audesp is not None else None,
                        "criterioJulgamento": item.criterio_julgamento,
                        "itemCategoria": item.item_categoria,
                        "patrimonio": item.patrimonio,
                        "codigoRegistroImobiliario": item.codigo_registro_imobiliario,
                    })
            lotes_licitacao_audesp_json.append({
                "numeroLote": lote.numero_lote,
                "descricaoLote": lote.descricao,
                "valorEstimadoLote": float(lote.valor_estimado_lote) if lote.valor_estimado_lote is not None else None,
                "itensDoLote": itens_do_lote_json,
            })

    dados_edital_audesp = {
        "descritor": descritor_json_limpo,
        "dataGeracaoDocumento": datetime.date.today().strftime("%Y-%m-%d"),
        "identificadorSoftware": "SysGov",
        "versaoSoftware": "1.0",
        "codigoUnidadeCompradora": edital.codigo_unidade_compradora,
        "tipoInstrumentoConvocatorio": edital.tipo_instrumento_convocatorio_audesp,
        "modalidade": edital.modalidade_audesp,
        "modoDisputa": edital.modo_disputa,
        "numeroCompra": edital.numero_compra_audesp,
        "anoCompra": edital.ano_compra_audesp,
        "numeroProcessoOrigem": edital.numero_processo_origem_audesp,
        "objetoCompra": edital.objeto_compra_audesp,
        "informacaoComplementar": edital.informacao_complementar,
        "srp": edital.srp,
        "dataEncerramentoProposta": edital.data_encerramento_proposta.strftime("%Y-%m-%dT%H:%M:%S") if edital.data_encerramento_proposta else None,
        "amparoLegal": edital.amparo_legal,
        "linkSistemaOrigem": edital.link_sistema_origem,
        "justificativaPresencial": edital.justificativa_presencial,
        "publicacoes": [], # <<< AGORA UMA LISTA VAZIA, POIS O MODELO FOI REMOVIDO DE licitacoes.models
        "itensCompra": itens_licitacao_audesp_json,
        "lotesCompra": lotes_licitacao_audesp_json,
    }

    dados_edital_audesp_limpo = {k: v for k, v in dados_edital_audesp.items() if v is not None and v != '' and (not isinstance(v, list) or len(v) > 0)}
    return JsonResponse(dados_edital_audesp_limpo, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})


# --- VIEWS DE DETALHES DE DOCUMENTOS AUDESP (UI) ---

@login_required
def detalhar_ajuste_contratual_audesp(request, pk):
    ajuste = get_object_or_404(AudespAjusteContratual, pk=pk)

    context = {
        'ajuste': ajuste,
        'titulo_pagina': f'Detalhes do Ajuste Contratual AUDESP: {ajuste.codigo_contrato_audesp}',
    }
    return render(request, 'integracao_audesp/detalhar_ajuste_contratual_audesp.html', context)


@login_required
def detalhar_ata_rp_audesp(request, pk):
    ata_rp = get_object_or_404(AudespAtaRegistroPrecos, pk=pk)

    context = {
        'ata_rp': ata_rp,
        'titulo_pagina': f'Detalhes da Ata de Registro de Preços AUDESP: {ata_rp.numero_ata_registro_preco}',
    }
    return render(request, 'integracao_audesp/detalhar_ata_rp_audesp.html', context)


@login_required
def detalhar_empenho_audesp(request, pk):
    empenho = get_object_or_404(AudespEmpenhoContrato, pk=pk)

    context = {
        'empenho': empenho,
        'titulo_pagina': f'Detalhes do Empenho de Contrato AUDESP: {empenho.numero_empenho}',
    }
    return render(request, 'integracao_audesp/detalhar_empenho_audesp.html', context)


# --- VIEWS DE GERAÇÃO DE JSON (API) ---

@login_required
def gerar_ajuste_contratual_audesp_json(request, ajuste_id):
    ajuste = get_object_or_404(AudespAjusteContratual, pk=ajuste_id)
    config_data = get_audesp_config_data()

    descritor_json = {
        "municipio": config_data["municipio_codigo"],
        "entidade": config_data["entidade_codigo"],
        "adesaoParticipacao": ajuste.adesao_participacao,
        "gerenciadoraJurisdicionada": ajuste.gerenciadora_jurisdicionada,
        "cnpjGerenciadora": ajuste.cnpj_gerenciadora,
        "municipioGerenciador": ajuste.municipio_gerenciador,
        "entidadeGerenciadora": ajuste.entidade_gerenciadora,
        "codigoEdital": ajuste.codigo_edital_audesp,
        "codigoAta": ajuste.codigo_ata_rp_audesp,
        "codigoContrato": ajuste.codigo_contrato_audesp,
        "retificacao": ajuste.retificacao
    }
    descritor_json_limpo = {k: v for k, v in descritor_json.items() if v is not None and v != '' and (not isinstance(v, list) or len(v) > 0)}

    dados_ajuste_contratual_audesp = {
        "descritor": descritor_json_limpo,
        "fonteRecursosContratacao": ajuste.fonte_recursos_contratacao if ajuste.fonte_recursos_contratacao else [],
        "itens": ajuste.itens_contratados_ids if ajuste.itens_contratados_ids else [],
        "tipoContratoId": ajuste.tipo_contrato_id,
        "numeroContratoEmpenho": ajuste.numero_contrato_empenho,
        "anoContrato": ajuste.ano_contrato,
        "processo": ajuste.processo_sistema_origem,
        "categoriaProcessoId": ajuste.categoria_processo_id,
        "receita": ajuste.receita,
        "despesas": ajuste.despesas_classificacao if ajuste.despesas_classificacao else [],
        "codigoUnidade": ajuste.codigo_unidade,
        "niFornecedor": ajuste.ni_fornecedor,
        "tipoPessoaFornecedor": ajuste.tipo_pessoa_fornecedor,
        "nomeRazaoSocialFornecedor": ajuste.nome_razao_social_fornecedor,
        "niFornecedorSubContratado": ajuste.ni_fornecedor_subcontratado,
        "tipoPessoaFornecedorSubContratado": ajuste.tipo_pessoa_fornecedor_subcontratado,
        "nomeRazaoSocialFornecedorSubContratado": ajuste.nome_razao_social_fornecedor_subcontratado,
        "objetoContrato": ajuste.objeto_contrato,
        "informacaoComplementar": ajuste.informacao_complementar,
        "valorInicial": float(ajuste.valor_inicial),
        "numeroParcelas": ajuste.numero_parcelas,
        "valorParcela": float(ajuste.valor_parcela) if ajuste.valor_parcela is not None else None,
        "valorGlobal": float(ajuste.valor_global),
        "valorAcumulado": float(ajuste.valor_acumulado),
        "dataAssinatura": ajuste.data_assinatura.strftime("%Y-%m-%d"),
        "dataVigenciaInicio": ajuste.data_vigencia_inicio.strftime("%Y-%m-%d"),
        "dataVigenciaFim": ajuste.data_vigencia_fim.strftime("%Y-%m-%d"),
        "vigenciaMeses": ajuste.vigencia_meses,
        "tipoObjetoContrato": ajuste.tipo_objeto_contrato
    }
    dados_ajuste_contratual_audesp_limpo = {k: v for k, v in dados_ajuste_contratual_audesp.items() if v is not None and v != '' and (not isinstance(v, list) or len(v) > 0)} # Corrigido para ser limpo
    return JsonResponse(dados_ajuste_contratual_audesp_limpo, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4}) # Usar a versão limpa


@login_required
def gerar_ata_rp_audesp_json(request, ata_rp_id):
    ata_rp = get_object_or_404(AudespAtaRegistroPrecos, pk=ata_rp_id)
    config_data = get_audesp_config_data()

    descritor_json = {
        "municipio": config_data["municipio_codigo"],
        "entidade": config_data["entidade_codigo"],
        "codigoEdital": ata_rp.codigo_edital_audesp,
        "codigoAta": ata_rp.codigo_ata_audesp,
        "anoCompra": ata_rp.ano_compra,
        "retificacao": ata_rp.retificacao
    }

    descritor_json_limpo = {k: v for k, v in descritor_json.items() if v is not None and v != '' and (not isinstance(v, list) or len(v) > 0)}

    dados_ata_rp_audesp = {
        "descritor": descritor_json_limpo,
        "numeroItem": ata_rp.itens_licitados_ids if ata_rp.itens_licitados_ids else [], # Array de números (IDs de itens)
        "numeroAtaRegistroPreco": ata_rp.numero_ata_registro_preco,
        "anoAta": ata_rp.ano_ata,
        "dataAssinatura": ata_rp.data_assinatura.strftime("%Y-%m-%d"),
        "dataVigenciaInicio": ata_rp.data_vigencia_inicio.strftime("%Y-%m-%d"),
        "dataVigenciaFim": ata_rp.data_vigencia_fim.strftime("%Y-%m-%d"),
    }

    dados_ata_rp_audesp_limpo = {k: v for k, v in dados_ata_rp_audesp.items() if v is not None and v != '' and (not isinstance(v, list) or len(v) > 0)} # Corrigido para ser limpo
    return JsonResponse(dados_ata_rp_audesp_limpo, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4}) # Usar a versão limpa

# --- NOVAS VIEWS PARA AudespAtaRegistroPrecos ---
@login_required
def criar_ata_rp_audesp(request, edital_id=None, processo_id=None): # <<< NOVA VIEW AQUI
    edital_ref = None
    processo_ref = None

    if edital_id:
        edital_ref = get_object_or_404(Edital, pk=edital_id)
        processo_ref = edital_ref.processo_vinculado
    elif processo_id:
        processo_ref = get_object_or_404(Processo, pk=processo_id)

    if request.method == 'POST':
        form = AudespAtaRegistroPrecosForm(request.POST)
        if hasattr(form, 'request'): # Passa o request para o formulário
            form.request = request
        if form.is_valid():
            ata_rp = form.save(commit=False)
            ata_rp.criado_por = request.user
            if edital_ref:
                ata_rp.edital_origem = edital_ref
            if processo_ref:
                ata_rp.processo_vinculado = processo_ref
            
            config_data = get_audesp_config_data()
            if not ata_rp.municipio: ata_rp.municipio = config_data["municipio_codigo"]
            if not ata_rp.entidade: ata_rp.entidade = config_data["entidade_codigo"]
            if edital_ref and not ata_rp.codigo_edital_audesp: ata_rp.codigo_edital_audesp = edital_ref.numero_edital
            
            ata_rp.save()
            messages.success(request, 'Ata de Registro de Preços AUDESP criada com sucesso!')
            return redirect('integracao_audesp:detalhar_ata_rp_audesp', pk=ata_rp.pk)
        else:
            messages.error(request, 'Erro ao criar Ata de Registro de Preços. Verifique o formulário.')
    else: # GET request
        initial_data = {}
        if edital_ref:
            initial_data['codigo_edital_audesp'] = edital_ref.numero_edital
            initial_data['ano_compra'] = edital_ref.ano_compra_audesp # ou edital_ref.data_publicacao.year
            initial_data['processo_vinculado'] = processo_ref.pk if processo_ref else None
        
        config_data = get_audesp_config_data()
        if not initial_data.get('municipio'): initial_data['municipio'] = config_data["municipio_codigo"]
        if not initial_data.get('entidade'): initial_data['entidade'] = config_data["entidade_codigo"]

        form = AudespAtaRegistroPrecosForm(initial=initial_data)
        if hasattr(form, 'request'): # Passa o request para o formulário
            form.request = request
        if request.user.is_authenticated:
            form.fields['criado_por'].initial = request.user.pk
            form.fields['criado_por'].widget.attrs['disabled'] = 'disabled'
            form.fields['criado_por'].widget.attrs['class'] = 'form-control-plaintext'

    context = {
        'form': form,
        'titulo_pagina': 'Criar Nova Ata de Registro de Preços AUDESP',
        'edital_ref': edital_ref,
        'processo_ref': processo_ref,
    }
    return render(request, 'integracao_audesp/criar_ata_rp_audesp.html', context)

# --- NOVAS VIEWS PARA AudespEmpenhoContrato ---
@login_required
def criar_empenho_audesp(request, ajuste_id=None, df_id=None, processo_id=None): # <<< NOVA VIEW AQUI
    ajuste_ref = None
    df_ref = None
    processo_ref = None

    if ajuste_id:
        ajuste_ref = get_object_or_404(AudespAjusteContratual, pk=ajuste_id)
        processo_ref = ajuste_ref.processo_vinculado
    elif df_id:
        df_ref = get_object_or_404(DocumentoFiscal, pk=df_id)
        processo_ref = df_ref.processo_vinculado
    elif processo_id:
        processo_ref = get_object_or_404(Processo, pk=processo_id)

    if request.method == 'POST':
        form = AudespEmpenhoContratoForm(request.POST)
        if hasattr(form, 'request'): # Passa o request para o formulário
            form.request = request
        if form.is_valid():
            empenho = form.save(commit=False)
            empenho.criado_por = request.user
            if ajuste_ref:
                empenho.ajuste_contratual_audesp = ajuste_ref
            if df_ref:
                empenho.documento_fiscal_origem = df_ref
            if processo_ref:
                empenho.processo_vinculado = processo_ref
            
            # Tenta preencher automaticamente os códigos do descritor
            config_data = get_audesp_config_data()
            if not empenho.municipio: empenho.municipio = config_data["municipio_codigo"]
            if not empenho.entidade: empenho.entidade = config_data["entidade_codigo"]
            if ajuste_ref and not empenho.codigo_contrato_audesp: empenho.codigo_contrato_audesp = ajuste_ref.codigo_contrato_audesp
            
            empenho.save()
            messages.success(request, 'Empenho de Contrato AUDESP criado com sucesso!')
            return redirect('integracao_audesp:detalhar_empenho_audesp', pk=empenho.pk)
        else:
            messages.error(request, 'Erro ao criar Empenho de Contrato. Verifique o formulário.')
    else: # GET request
        initial_data = {}
        if ajuste_ref:
            initial_data['codigo_contrato_audesp'] = ajuste_ref.codigo_contrato_audesp
            initial_data['processo_vinculado'] = processo_ref.pk if processo_ref else None
            # Tentar preencher outros campos relevantes do ajuste
            initial_data['municipio'] = ajuste_ref.municipio # Exemplo
        elif df_ref:
            initial_data['numero_empenho'] = df_ref.nota_empenho_numero # Exemplo
            initial_data['ano_empenho'] = df_ref.nota_empenho_data_emissao.year if df_ref.nota_empenho_data_emissao else None
            initial_data['data_emissao_empenho'] = df_ref.nota_empenho_data_emissao
            initial_data['processo_vinculado'] = processo_ref.pk if processo_ref else None
        elif processo_ref:
            initial_data['processo_sistema_origem'] = processo_ref.numero_protocolo
            initial_data['processo_vinculado'] = processo_ref.pk

        # Preenche os códigos de município e entidade do descritor
        config_data = get_audesp_config_data()
        if not initial_data.get('municipio'): initial_data['municipio'] = config_data["municipio_codigo"]
        if not initial_data.get('entidade'): initial_data['entidade'] = config_data["entidade_codigo"]

        form = AudespEmpenhoContratoForm(initial=initial_data)
        if hasattr(form, 'request'): # Passa o request para o formulário
            form.request = request
        if request.user.is_authenticated:
            form.fields['criado_por'].initial = request.user.pk
            form.fields['criado_por'].widget.attrs['disabled'] = 'disabled'
            form.fields['criado_por'].widget.attrs['class'] = 'form-control-plaintext'

    context = {
        'form': form,
        'titulo_pagina': 'Criar Novo Empenho de Contrato AUDESP',
        'ajuste_ref': ajuste_ref,
        'df_ref': df_ref,
        'processo_ref': processo_ref,
    }
    return render(request, 'integracao_audesp/criar_empenho_audesp.html', context)


@login_required
def editar_empenho_audesp(request, pk): # <<< NOVA VIEW AQUI
    empenho = get_object_or_404(AudespEmpenhoContrato, pk=pk)
    if empenho.criado_por != request.user and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para editar este Empenho de Contrato AUDESP.")
        return redirect('integracao_audesp:detalhar_empenho_audesp', pk=empenho.pk)

    if request.method == 'POST':
        form = AudespEmpenhoContratoForm(request.POST, instance=empenho)
        if hasattr(form, 'request'): # Passa o request para o formulário
            form.request = request
        if form.is_valid():
            form.save()
            messages.success(request, 'Empenho de Contrato AUDESP atualizado com sucesso!')
            return redirect('integracao_audesp:detalhar_empenho_audesp', pk=empenho.pk)
        else:
            messages.error(request, 'Erro ao atualizar Empenho de Contrato. Verifique o formulário.')
    else: # GET request
        form = AudespEmpenhoContratoForm(instance=empenho)
        if hasattr(form, 'request'): # Passa o request para o formulário
            form.request = request
        form.fields['criado_por'].widget.attrs['disabled'] = 'disabled'
        form.fields['criado_por'].widget.attrs['class'] = 'form-control-plaintext'
        
    context = {
        'form': form,
        'empenho': empenho,
        'titulo_pagina': f'Editar Empenho de Contrato AUDESP: {empenho.numero_empenho}',
    }
    return render(request, 'integracao_audesp/editar_empenho_audesp.html', context)


@login_required
def editar_ata_rp_audesp(request, pk): # <<< NOVA VIEW AQUI
    ata_rp = get_object_or_404(AudespAtaRegistroPrecos, pk=pk)
    if ata_rp.criado_por != request.user and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para editar esta Ata de Registro de Preços AUDESP.")
        return redirect('integracao_audesp:detalhar_ata_rp_audesp', pk=ata_rp.pk)

    if request.method == 'POST':
        form = AudespAtaRegistroPrecosForm(request.POST, instance=ata_rp)
        if hasattr(form, 'request'): # Passa o request para o formulário
            form.request = request
        if form.is_valid():
            form.save()
            messages.success(request, 'Ata de Registro de Preços AUDESP atualizada com sucesso!')
            return redirect('integracao_audesp:detalhar_ata_rp_audesp', pk=ata_rp.pk)
        else:
            messages.error(request, 'Erro ao atualizar Ata de Registro de Preços. Verifique o formulário.')
    else: # GET request
        form = AudespAtaRegistroPrecosForm(instance=ata_rp)
        if hasattr(form, 'request'): # Passa o request para o formulário
            form.request = request
        form.fields['criado_por'].widget.attrs['disabled'] = 'disabled'
        form.fields['criado_por'].widget.attrs['class'] = 'form-control-plaintext'
        
    context = {
        'form': form,
        'ata_rp': ata_rp,
        'titulo_pagina': f'Editar Ata de Registro de Preços AUDESP: {ata_rp.numero_ata_registro_preco}',
    }
    return render(request, 'integracao_audesp/editar_ata_rp_audesp.html', context)


@login_required
def gerar_empenho_audesp_json(request, empenho_id):
    empenho = get_object_or_404(AudespEmpenhoContrato, pk=empenho_id)
    config_data = get_audesp_config_data()

    # --- Mapeamento do Schema JSON de Empenho de Contrato ---
    descritor_json = {
        "municipio": config_data["municipio_codigo"],
        "entidade": config_data["entidade_codigo"],
        "codigoContrato": empenho.codigo_contrato_audesp,
        "retificacao": empenho.retificacao
    }
    descritor_json_limpo = {k: v for k, v in descritor_json.items() if v is not None and v != '' and (not isinstance(v, list) or len(v) > 0)}

    dados_empenho_audesp = {
        "descritor": descritor_json_limpo,
        "numeroEmpenho": empenho.numero_empenho,
        "anoEmpenho": empenho.ano_empenho,
        "dataEmissaoEmpenho": empenho.data_emissao_empenho.strftime("%Y-%m-%d")
    }

    dados_empenho_audesp_limpo = {k: v for k, v in dados_empenho_audesp.items() if v is not None and v != '' and (not isinstance(v, list) or len(v) > 0)} # Corrigido para ser limpo
    return JsonResponse(dados_empenho_audesp_limpo, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4}) # Usar a versão limpa


# --- VIEWS DE LISTAGEM DE SUBMISSÕES AUDESP ---
@login_required
def listar_submissoes_audesp(request):
    submissoes = SubmissaoAudesp.objects.all().order_by('-data_submissao')
    context = {
        'titulo_pagina': 'Histórico de Submissões AUDESP',
        'submissoes': submissoes,
    }
    return render(request, 'integracao_audesp/listar_submissoes.html', context)


# integracao_audesp/mock_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def mock_audesp_login(request):
    """Simula o endpoint de login da API do AUDESP."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            logger.info(f"Mock Login: Tentativa de login para {email}")

            # Simule uma autenticação básica. Em um ambiente real, você validaria as credenciais.
            if email == 'teste@exemplo.com' and password == 'senha123':
                # Gerar um token de exemplo que seria usado em requisições futuras
                mock_token = "mock_access_token_1234567890abcdef"
                return JsonResponse({
                    'access_token': mock_token,
                    'token_type': 'Bearer',
                    'expires_in': 3600 # 1 hora
                }, status=200)
            else:
                return JsonResponse({'error': 'Credenciais inválidas'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Requisição JSON inválida'}, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def mock_audesp_enviar_pacote(request, schema_type):
    """Simula o endpoint de envio de pacotes da API do AUDESP."""
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer mock_access_token'):
            return JsonResponse({'error': 'Autenticação JWT inválida ou ausente'}, status=401)

        try:
            data = json.loads(request.body)
            logger.info(f"Mock Envio de Pacote ({schema_type}): Recebido JSON. Tamanho: {len(request.body)} bytes")

            # Aqui você pode adicionar lógica para validar o JSON contra o schema real
            # Por agora, vamos apenas simular sucesso ou um erro básico.

            # Exemplo: Se o JSON contiver a palavra "erro_simulado", retorne erro
            if "erro_simulado" in request.body.decode('utf-8').lower():
                 return JsonResponse({
                    'status': 'erro',
                    'mensagem': f'Erro simulado na validação do schema {schema_type}',
                    'detalhes': ['Campo X inválido', 'Formato Y incorreto']
                }, status=422) # 422 Unprocessable Entity é comum para erros de validação

            return JsonResponse({
                'status': 'sucesso',
                'mensagem': f'Pacote de {schema_type} recebido e validado (mock).',
                'protocolo': f'MOCK-{schema_type}-XYZ123ABC'
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Requisição JSON inválida'}, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


# integracao_audesp/views.py (Exemplo para uma view que gera JSON de Edital)
from django.http import JsonResponse
from .utils import validate_json_with_schema
# ... outras imports ...

def gerar_edital_detalhado_audesp_json(request):
    # ... sua lógica atual para criar o dicionário edital_json_data ...

    is_valid, errors = validate_json_with_schema(edital_json_data, 'audesp_edital_v4.json')

    if not is_valid:
        # Se o JSON não for válido contra o schema, você pode:
        # 1. Logar os erros para depuração.
        # 2. Retornar um erro para o usuário (em ambiente de desenvolvimento/teste).
        # 3. Levantar uma exceção para interromper o processo.
        print("Erros de validação do JSON:", errors) # Para fins de depuração
        return JsonResponse({'status': 'erro', 'mensagem': 'JSON gerado inválido contra schema', 'detalhes': errors}, status=400)

    # Se for válido, você pode converter para string e enviar para o mock
    json_string = json.dumps(edital_json_data, indent=2)

    # Agora, em vez de retornar direto, você chamaria a API (o mock, por enquanto)
    # Exemplo (você criará a função de envio de fato depois):
    # response_from_mock = send_json_to_audesp_api(json_string, 'licitacoes-v4') # Função a ser criada

    return JsonResponse({'status': 'ok', 'message': 'JSON gerado e validado com sucesso (pronto para envio mockado)'})


# integracao_audesp/views.py (Exemplo)
import json
from django.http import JsonResponse
# Importe sua função de validação
from .utils import validate_json_with_schema

def gerar_e_validar_edital(request):
    # 1. Sua lógica existente para gerar o dicionário Python do edital
    edital_json_data = {
        "identificacao": "EDT-2025-001",
        "tipo_edital": "Eletronico",
        "data_abertura": "2025-08-06",
        "objeto": "Contratacao de servicos de consultoria...",
        # ... seus outros campos do Edital Detalhado
    }

    # 2. Validar o dicionário contra o schema
    is_valid, errors = validate_json_with_schema(edital_json_data, 'audesp_edital_v4.json') # Verifique o nome exato do seu arquivo de schema!

    if not is_valid:
        print("Erro de validação interna do JSON:", errors)
        return JsonResponse({
            'status': 'erro_validacao_interna',
            'mensagem': 'JSON gerado não está em conformidade com o schema do TCE-SP.',
            'detalhes': errors
        }, status=400)

    # Se chegou aqui, o JSON é válido internamente.
    # Agora, você pode convertê-lo para string e passar para a função de envio
    json_payload = json.dumps(edital_json_data, indent=2)

    # 3. Chamar a função que simula o envio para a API (próximo passo)
    response_from_mock = enviar_json_para_mock_audesp(json_payload, 'edital-detalhado')

    # Retornar a resposta do mock para a interface
    return JsonResponse(response_from_mock.json(), status=response_from_mock.status_code)



# integracao_audesp/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import validate_json_with_schema # Importa sua função de validação
from .api_client import get_mock_audesp_token, enviar_json_para_mock_audesp # Importa as funções do cliente API

@csrf_exempt
def enviar_edital_para_audesp_mock(request):
    if request.method == 'POST':
        try:
            # 1. Obter os dados do Edital (simulação de como viria do formulário ou DB)
            # Para este exemplo, vamos usar um dado fixo. Na realidade, viria de um form/model.
            edital_json_data = {
                "identificacao": "EDT-2025-001",
                "tipo_edital": "Eletronico",
                "data_abertura": "2025-08-06",
                "objeto": "Contratacao de servicos de consultoria para projeto X.",
                "valor_estimado": 150000.00,
                "modalidade": "Pregao Eletronico",
                "situacao": "Publicado",
                "link_edital": "http://seusysgov.com.br/editais/edt-2025-001.pdf",
                # Adicione um campo para testar erro simulado no mock, se quiser:
                # "campo_para_erro": "erro_simulado"
            }
            # Se quiser testar um JSON inválido para o TCE, descomente e altere:
            # edital_json_data['data_abertura'] = 'data-invalida' # Exemplo de dado inválido para o schema

            # 2. Validar o JSON localmente com o schema do TCE
            is_valid, errors = validate_json_with_schema(edital_json_data, 'audesp_edital_v4.json')
            if not is_valid:
                print("Validação LOCAL falhou:", errors)
                return JsonResponse({
                    'status': 'falha_local',
                    'mensagem': 'JSON gerado não está em conformidade com o schema local.',
                    'detalhes': errors
                }, status=400)

            # Se válido localmente, converte para string
            json_payload = json.dumps(edital_json_data, indent=2)

            # 3. Obter token do mock da API
            login_response = get_mock_audesp_token('teste@exemplo.com', 'senha123')
            if login_response is None or not login_response.ok:
                return JsonResponse({'status': 'erro_autenticacao', 'mensagem': 'Não foi possível obter token do mock da API.', 'detalhes': login_response.json() if login_response else 'N/A'}, status=500)
            
            token = login_response.json().get('access_token')
            if not token:
                 return JsonResponse({'status': 'erro_token', 'mensagem': 'Token não recebido do mock de login.'}, status=500)

            # 4. Enviar o JSON para o mock da API do TCE-SP
            api_response = enviar_json_para_mock_audesp(json_payload, 'edital-detalhado', token)

            if api_response is None:
                return JsonResponse({'status': 'erro_conexao_mock', 'mensagem': 'Erro de conexão ou resposta inválida do mock da API.'}, status=500)

            # 5. Retornar a resposta do mock para o cliente/navegador
            return JsonResponse(api_response.json(), status=api_response.status_code)

        except Exception as e:
            print(f"Erro inesperado na view: {e}")
            return JsonResponse({'status': 'erro_interno', 'mensagem': f'Erro inesperado: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Método não permitido'}, status=405)