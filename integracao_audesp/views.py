# SysGov_Project/integracao_audesp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

# Importações de Modelos
from .models import AudespConfiguracao, SubmissaoAudesp
from contratacoes.models import ETP, Contrato
from licitacoes.models import Edital
from financeiro.models import DocumentoFiscal, Pagamento

# --- PAINEL E HISTÓRICO ---

@login_required
def painel_audesp_view(request):
    """ Encontra e exibe todos os documentos pendentes de submissão ao AUDESP. """
    # Lógica para encontrar ETPs pendentes
    etp_content_type = ContentType.objects.get_for_model(ETP)
    etps_submetidos_ids = SubmissaoAudesp.objects.filter(content_type=etp_content_type).values_list('object_id', flat=True)
    etps_pendentes = ETP.objects.filter(status='APROVADO').exclude(pk__in=etps_submetidos_ids)

    # Lógica para encontrar Editais pendentes
    edital_content_type = ContentType.objects.get_for_model(Edital)
    editais_submetidos_ids = SubmissaoAudesp.objects.filter(content_type=edital_content_type).values_list('object_id', flat=True)
    editais_pendentes = Edital.objects.filter(status__in=['PUBLICADO', 'HOMOLOGADO']).exclude(pk__in=editais_submetidos_ids)

    # Lógica para encontrar Contratos pendentes
    contrato_content_type = ContentType.objects.get_for_model(Contrato)
    contratos_submetidos_ids = SubmissaoAudesp.objects.filter(content_type=contrato_content_type).values_list('object_id', flat=True)
    contratos_pendentes = Contrato.objects.filter(status='VIGENTE').exclude(pk__in=contratos_submetidos_ids)
    
    # Lógica para Documentos Fiscais e Pagamentos
    df_content_type = ContentType.objects.get_for_model(DocumentoFiscal)
    df_submetidos_ids = SubmissaoAudesp.objects.filter(content_type=df_content_type).values_list('object_id', flat=True)
    documentos_fiscais_pendentes = DocumentoFiscal.objects.all().exclude(pk__in=df_submetidos_ids)

    pg_content_type = ContentType.objects.get_for_model(Pagamento)
    pg_submetidos_ids = SubmissaoAudesp.objects.filter(content_type=pg_content_type).values_list('object_id', flat=True)
    pagamentos_pendentes = Pagamento.objects.all().exclude(pk__in=pg_submetidos_ids)

    context = {
        'etps_pendentes': etps_pendentes,
        'editais_pendentes': editais_pendentes,
        'contratos_pendentes': contratos_pendentes,
        'documentos_fiscais_pendentes': documentos_fiscais_pendentes,
        'pagamentos_pendentes': pagamentos_pendentes,
        'titulo_pagina': 'Painel de Submissão AUDESP'
    }
    return render(request, 'integracao_audesp/painel_audesp.html', context)

@login_required
def listar_submissoes_audesp(request):
    """ Exibe o histórico de todas as submissões geradas. """
    submissoes = SubmissaoAudesp.objects.all().order_by('-data_submissao')
    context = {'submissoes': submissoes, 'titulo_pagina': 'Histórico de Submissões AUDESP'}
    return render(request, 'integracao_audesp/listar_submissoes.html', context)


# --- VIEWS DE GERAÇÃO DE JSON ---

def get_audesp_config_data():
    """ Função auxiliar para buscar os dados de configuração. """
    try:
        config = AudespConfiguracao.objects.first()
        if config:
            return {
                "municipio_codigo": config.municipio_codigo_audesp,
                "entidade_codigo": config.entidade_codigo_audesp
            }
    except AudespConfiguracao.DoesNotExist:
        pass
    return {"municipio_codigo": 0, "entidade_codigo": 0}

@login_required
def gerar_etp_audesp_json(request, etp_id):
    etp = get_object_or_404(ETP, pk=etp_id)
    # ... Sua lógica de gerar JSON do ETP ...
    return JsonResponse({"message": "JSON do ETP gerado com sucesso."})

@login_required
def gerar_edital_audesp_json(request, edital_id):
    edital = get_object_or_404(Edital, pk=edital_id)
    # ... Sua lógica de gerar JSON do Edital ...
    return JsonResponse({"message": "JSON do Edital gerado com sucesso."})

@login_required
def gerar_contrato_audesp_json(request, contrato_id):
    contrato = get_object_or_404(Contrato, pk=contrato_id)
    config_data = get_audesp_config_data()
    # ... Lógica de mapeamento do Contrato para o JSON de Ajuste ...
    dados_json = { "exemplo": "dados_do_contrato" } # Substituir pela sua lógica completa
    return JsonResponse(dados_json, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})
