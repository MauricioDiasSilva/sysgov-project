

import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Avg, Count, Q, F
from django.forms import inlineformset_factory
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.core.serializers import serialize
import json
from django.contrib.auth.models import User
from django.conf import settings 
from contratacoes.models import Contrato 
from core.models import Processo
from .models import DocumentoFiscal, Pagamento 
from .forms import DocumentoFiscalForm, PagamentoForm,NotaEmpenhoForm 

# --- Views de Dashboard e Listagens ---
@login_required
def financeiro_dashboard(request):
    documentos_fiscais_recentes = DocumentoFiscal.objects.order_by('-documento_fiscal_data_emissao')[:5]
    pagamentos_recentes = Pagamento.objects.order_by('-nota_fiscal_pagto_dt')[:5]
    context = {
        'documentos_fiscais_recentes': documentos_fiscais_recentes,
        'pagamentos_recentes': pagamentos_recentes,
        'titulo_pagina': 'Dashboard Financeiro'
    }
    return render(request, 'financeiro/dashboard.html', context)

@login_required
def listar_documentos_fiscais(request):
    documentos = DocumentoFiscal.objects.all().order_by('-documento_fiscal_data_emissao')
    context = {'documentos': documentos, 'titulo_pagina': 'Documentos Fiscais'}
    return render(request, 'financeiro/listar_documentos.html', context)

@login_required
def listar_pagamentos(request):
    pagamentos = Pagamento.objects.all().order_by('-nota_fiscal_pagto_dt')
    context = {'pagamentos': pagamentos, 'titulo_pagina': 'Listar Pagamentos'}
    return render(request, 'financeiro/listar_pagamentos.html', context)

# --- Views de Detalhes e Edição ---
@login_required
def detalhar_documento_fiscal(request, pk):
    df = get_object_or_404(DocumentoFiscal, pk=pk)
    # Verificação de permissão do usuário
    if df.processo_vinculado and df.processo_vinculado.usuario != request.user and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para visualizar este Documento Fiscal.")
        return redirect('financeiro:dashboard_financeiro')
    context = {'documento': df, 'titulo_pagina': f'Detalhes DF: {df.documento_fiscal_numero}'}
    return render(request, 'financeiro/detalhar_documento.html', context)

@login_required
@permission_required('financeiro.change_documentofiscal', raise_exception=True)
def editar_documento_fiscal(request, pk):
    df = get_object_or_404(DocumentoFiscal, pk=pk)
    if df.processo_vinculado and df.processo_vinculado.usuario != request.user and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para editar este Documento Fiscal.")
        return redirect('financeiro:detalhar_documento_fiscal', pk=df.pk)

    if request.method == 'POST':
        form = DocumentoFiscalForm(request.POST, instance=df)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento Fiscal atualizado com sucesso!')
            return redirect('financeiro:detalhar_documento_fiscal', pk=df.pk)
        else:
            messages.error(request, 'Erro ao atualizar Documento Fiscal. Verifique os campos.')
    else:
        form = DocumentoFiscalForm(instance=df)
    context = {
        'form': form,
        'documento': df,
        'titulo_pagina': f'Editar DF: {df.documento_fiscal_numero}'
    }
    return render(request, 'financeiro/editar_documento_fiscal.html', context)

@login_required
def detalhar_pagamento(request, pk):
    pg = get_object_or_404(Pagamento, pk=pk)
    if pg.processo_vinculado and pg.processo_vinculado.usuario != request.user and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para visualizar este Pagamento.")
        return redirect('financeiro:dashboard_financeiro')
    context = {'pagamento': pg, 'titulo_pagina': f'Detalhes Pagto: {pg.documento_fiscal_numero}'}
    return render(request, 'financeiro/detalhar_pagamento.html', context)

@login_required
@permission_required('financeiro.change_pagamento', raise_exception=True)
def editar_pagamento(request, pk):
    pg = get_object_or_404(Pagamento, pk=pk)
    if pg.processo_vinculado and pg.processo_vinculado.usuario != request.user and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para editar este Pagamento.")
        return redirect('financeiro:detalhar_pagamento', pk=pg.pk)

    if request.method == 'POST':
        form = PagamentoForm(request.POST, instance=pg)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pagamento atualizado com sucesso!')
            return redirect('financeiro:detalhar_pagamento', pk=pg.pk)
        else:
            messages.error(request, 'Erro ao atualizar Pagamento. Verifique os campos.')
    else:
        form = PagamentoForm(instance=pg)
    context = {
        'form': form,
        'pagamento': pg,
        'titulo_pagina': f'Editar Pagamento: {pg.documento_fiscal_numero}'
    }
    return render(request, 'financeiro/editar_pagamento.html', context)

# --- Views de Criação e Vinculação ---
@login_required
def gerar_xml_documento_fiscal(request, processo_id=None):
    processo_core = None
    if processo_id:
        processo_core = get_object_or_404(Processo, id=processo_id)

    if request.method == 'POST':
        form = DocumentoFiscalForm(request.POST)
        if form.is_valid():
            df = form.save(commit=False)
            if processo_core:
                df.processo_vinculado = processo_core 
            df.save()
            messages.success(request, 'Documento Fiscal registrado com sucesso!')
            if processo_core:
                return redirect('detalhes_processo', processo_id=processo_core.id)
            else:
                return redirect('financeiro:detalhar_documento_fiscal', pk=df.pk)
        else:
            messages.error(request, 'Erro ao registrar Documento Fiscal. Verifique os campos.')
    else:
        initial_data = {}
        if processo_core:
            initial_data['codigo_ajuste'] = processo_core.numero_protocolo
            initial_data['nota_empenho_numero'] = processo_core.titulo
        form = DocumentoFiscalForm(initial=initial_data)

    context = {
        'form': form,
        'processo_core': processo_core,
        'titulo_pagina': 'Registrar Documento Fiscal'
    }
    return render(request, 'financeiro/gerar_df.html', context)


@login_required
def gerar_xml_pagamento(request, processo_id=None):
    processo_core = None
    if processo_id:
        processo_core = get_object_or_404(Processo, id=processo_id)

    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            pg = form.save(commit=False)
            if processo_core:
                pg.processo_vinculado = processo_core
            pg.save()
            messages.success(request, 'Pagamento registrado com sucesso!')
            if processo_core:
                return redirect('detalhes_processo', processo_id=processo_core.id)
            else:
                return redirect('financeiro:detalhar_pagamento', pk=pg.pk)
        else:
            messages.error(request, 'Erro ao registrar Pagamento. Verifique os campos.')
    else:
        initial_data = {}
        if processo_core:
             pass
        form = PagamentoForm(initial=initial_data)

    context = {
        'form': form,
        'processo_core': processo_core,
        'titulo_pagina': 'Registrar Pagamento'
    }
    return render(request, 'financeiro/gerar_pg.html', context)

# --- Funções Auxiliares para Geração de XML e Download ---
def gerar_xml_df_content(df):
    xml_content = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
    <DocumentoFiscal xmlns="http://www.tce.sp.gov.br/audesp/xml/documentofiscal"
    xmlns:gen="http://www.tce.sp.gov.br/audesp/xml/generico"
    xmlns:tag="http://www.tce.sp.gov.br/audesp/xml/tagcomum"
    xsi:schemaLocation="http://www.tce.sp.gov.br/audesp/xml/documentofiscal ../documentofiscal/AUDESP4_DOCUMENTOFISCAL_2025_A.XSD"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    {gerar_descritor_xml('DOCUMENTOFISCAL')}
    <ArrayDocumentoFiscal>
        <CodigoAjuste>{df.codigo_ajuste}</CodigoAjuste>
        <DocFiscal>
            <MedicaoNumero>{df.medicao_numero}</MedicaoNumero>
            <NotaEmpenhoNumero>{df.nota_empenho_numero}</NotaEmpenhoNumero>
            <NotaEmpenhoDataEmissao>{df.nota_empenho_data_emissao.strftime('%Y-%m-%d')}</NotaEmpenhoDataEmissao>
            <DocumentoFiscalNumero>{df.documento_fiscal_numero}</DocumentoFiscalNumero>
            <DocumentoFiscalUF>{df.documento_fiscal_uf}</DocumentoFiscalUF>
            <DocumentoFiscalValor>{df.documento_fiscal_valor:.2f}</DocumentoFiscalValor>
            <DocumentoFiscalDataEmissao>{df.documento_fiscal_data_emissao.strftime('%Y-%m-%d')}</DocumentoFiscalDataEmissao>
        </DocFiscal>
    </ArrayDocumental>
    </DocumentoFiscal>
    """
    return xml_content

def gerar_xml_pg_content(pg):
    xml_content = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
    <Pagamento xmlns="http://www.tce.sp.gov.br/audesp/xml/pagamento"
    xmlns:gen="http://www.tce.sp.gov.br/audesp/xml/generico"
    xmlns:tag="http://www.tce.sp.gov.br/audesp/xml/tagcomum"
    xsi:schemaLocation="http://www.tce.sp.gov.br/audesp/xml/pagamento ../pagamento/AUDESP4_PAGAMENTO_2025_A.XSD"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    {gerar_descritor_xml('PAGAMENTO')}
    <ArrayPagamento>
    <CodigoAjuste>{pg.codigo_ajuste}</CodigoAjuste>
    <Pagto>
        <MedicaoNumero>{pg.medicao_numero}</MedicaoNumero>
        <NotaEmpenhoNumero>{pg.nota_empenho_numero}</NotaEmpenhoNumero>
        <NotaEmpenhoDataEmissao>{pg.nota_empenho_data_emissao.strftime('%Y-%m-%d')}</NotaEmpenhoDataEmissao>
        <DocumentoFiscalNumero>{pg.documento_fiscal_numero}</DocumentoFiscalNumero>
        <DocumentoFiscalDataEmissao>{pg.documento_fiscal_data_emissao.strftime('%Y-%m-%d')}</DocumentoFiscalDataEmissao>
        <DocumentoFiscalUF>{pg.documento_fiscal_uf}</DocumentoFiscalUF>
        <NotaFiscalValorPago>{pg.nota_fiscal_valor_pago:.2f}</NotaFiscalValorPago>
        <NotaFiscalPagtoDt>{pg.nota_fiscal_pagto_dt.strftime('%Y-%m-%d')}</NotaFiscalPagtoDt>
        <RecolhidoEncargosPrevidenciario>{pg.recolhido_encargos_previdenciario if pg.recolhido_encargos_previdenciario else 'N'}</RecolhidoEncargosPrevidenciario>
    </Pagto>
    </ArrayPagamento>
    </Pagamento>
    """
    return xml_content


@login_required
def download_df_xml(request, pk):
    df = get_object_or_404(DocumentoFiscal, pk=pk)
    # Garante que o documento fiscal está vinculado a um processo do usuário logado
    if not df.processo_vinculado or df.processo_vinculado.usuario != request.user:
        messages.error(request, "Você não tem permissão para baixar este documento.")
        return redirect('financeiro:listar_documentos_fiscais')

    xml_content = gerar_xml_df_content(df)
    response = HttpResponse(xml_content, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="documento_fiscal_{df.pk}.xml"'
    return response

@login_required
def download_pg_xml(request, pk):
    pg = get_object_or_404(Pagamento, pk=pk)
    # Garante que o pagamento está vinculado a um processo do usuário logado
    if not pg.processo_vinculado or pg.processo_vinculado.usuario != request.user:
        messages.error(request, "Você não tem permissão para baixar este pagamento.")
        return redirect('financeiro:listar_pagamentos')
    
    xml_content = gerar_xml_pg_content(pg)
    response = HttpResponse(xml_content, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="pagamento_{pg.pk}.xml"'
    return response


# SysGov_Project/sysgov_project/financeiro/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from licitacoes.models import Edital # <<< Importe o modelo Edital

@login_required
def gerar_edital_audesp_json(request, edital_id):
    edital = get_object_or_404(Edital, pk=edital_id)

    # Lógica de segurança: verifica se o usuário logado tem permissão
    # Superusuários podem ignorar as restrições
    if not request.user.is_superuser:
        # Se não for superusuário, verifique se ele é o responsável pelo processo ou tem permissão
        if edital.processo_vinculado and edital.processo_vinculado.usuario != request.user:
             return JsonResponse({'error': 'Você não tem permissão para acessar este Edital.'}, status=403)
        # Se você tiver uma permissão específica para "gerar json", adicione a verificação aqui
        # if not request.user.has_perm('financeiro.gerar_edital_audesp_json'):
        #     return JsonResponse({'error': 'Você não tem permissão para gerar o JSON.'}, status=403)

    # ... (restante da view para gerar o JSON) ...
    # Lógica de negócio para gerar o JSON
    edital_json_data = {
        "Descritor": {
            "AnoExercicio": edital.data_publicacao.year,
            "TipoDocumento": "EDITAL",
            "Entidade": "1",
            "Municipio": "6300",
            "DataCriacaoXML": edital.data_publicacao.strftime('%Y-%m-%d')
        },
        "Edital": {
            "NumeroEdital": edital.numero_edital,
            "ObjetoLicitacao": edital.titulo,
            "ValorEstimado": str(edital.valor_estimado),
            "LinkEditalCompleto": edital.link_edital_completo,
        }
    }

    response = JsonResponse(edital_json_data, safe=False)
    response['Content-Disposition'] = f'attachment; filename="audesp_edital_{edital.pk}.json"'
    return response



# SysGov_Project/financeiro/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Pagamento # Importe o modelo Pagamento
from .forms import PagamentoForm # Importe o formulário PagamentoForm

# ... (todas as suas outras views) ...

# --- NOVA VIEW PARA EDITAR PAGAMENTO ---
@login_required
@permission_required('financeiro.change_pagamento', raise_exception=True)
def editar_pagamento(request, pk):
    pagamento = get_object_or_404(Pagamento, pk=pk)

    # Opcional: Verificação adicional de permissão se o usuário é o responsável pelo processo/pagamento
    if pagamento.processo_vinculado and pagamento.processo_vinculado.usuario != request.user and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para editar este Pagamento.")
        return redirect('financeiro:detalhar_pagamento', pk=pagamento.pk)

    if request.method == 'POST':
        form = PagamentoForm(request.POST, instance=pagamento) # Usa a instância para pré-preencher
        if form.is_valid():
            form.save()
            messages.success(request, 'Pagamento atualizado com sucesso!')
            return redirect('financeiro:detalhar_pagamento', pk=pagamento.pk)
        else:
            messages.error(request, 'Erro ao atualizar Pagamento. Verifique os campos.')
    else: # GET request
        form = PagamentoForm(instance=pagamento)

    context = {
        'form': form,
        'pagamento': pagamento,
        'titulo_pagina': f'Editar Pagamento: {pagamento.documento_fiscal_numero}'
    }
    return render(request, 'financeiro/editar_pagamento.html', context)



# Em financeiro/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import NotaEmpenhoForm # Crie ou adicione a esta importação
from contratacoes.models import Contrato # Precisamos do modelo Contrato

# ... (suas outras views de financeiro) ...

@login_required
def criar_empenho(request, contrato_id):
    contrato = get_object_or_404(Contrato, pk=contrato_id)
    
    if request.method == 'POST':
        form = NotaEmpenhoForm(request.POST)
        if form.is_valid():
            empenho = form.save(commit=False)
            empenho.contrato = contrato
            empenho.fornecedor = contrato.contratado # Puxa o fornecedor diretamente do contrato
            empenho.save()
            messages.success(request, f"Nota de Empenho {empenho.numero_empenho}/{empenho.ano_empenho} criada com sucesso!")
            return redirect('contratacoes:detalhar_contrato', pk=contrato.pk) # Volta para os detalhes do contrato
    else:
        form = NotaEmpenhoForm()
        
    context = {
        'form': form,
        'contrato': contrato,
        'titulo_pagina': f'Adicionar Empenho ao Contrato {contrato.numero_contrato}/{contrato.ano_contrato}'
    }
    return render(request, 'financeiro/criar_empenho.html', context)

# Em financeiro/views.py
from .models import NotaEmpenho # Adicione esta importação

# ...

@login_required
def listar_empenhos(request):
    empenhos = NotaEmpenho.objects.all().order_by('-data_emissao')
    context = {
        'empenhos': empenhos,
        'titulo_pagina': 'Notas de Empenho Emitidas'
    }
    return render(request, 'financeiro/listar_empenhos.html', context)

# Em financeiro/views.py

@login_required
def detalhar_empenho(request, pk):
    empenho = get_object_or_404(NotaEmpenho, pk=pk)
    context = {
        'empenho': empenho,
        'titulo_pagina': f'Detalhes do Empenho {empenho.numero_empenho}/{empenho.ano_empenho}'
    }
    return render(request, 'financeiro/detalhar_empenho.html', context)

# Em financeiro/views.py

@login_required
def editar_empenho(request, pk):
    empenho = get_object_or_404(NotaEmpenho, pk=pk)
    
    if request.method == 'POST':
        form = NotaEmpenhoForm(request.POST, instance=empenho)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nota de Empenho atualizada com sucesso!')
            return redirect('financeiro:detalhar_empenho', pk=empenho.pk)
    else:
        form = NotaEmpenhoForm(instance=empenho)
        
    context = {
        'form': form,
        'empenho': empenho,
        'titulo_pagina': f'Editar Empenho {empenho.numero_empenho}/{empenho.ano_empenho}'
    }
    return render(request, 'financeiro/editar_empenho.html', context)