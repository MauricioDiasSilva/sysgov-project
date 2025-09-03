# SysGov_Project/integracao_audesp/urls.py

from django.urls import path
from . import views

app_name = 'integracao_audesp'

urlpatterns = [
    # Módulo: Histórico de Submissões AUDESP (Ponto de Entrada)
    
    path('painel/', views.painel_audesp_view, name='painel_audesp'),
    path('submissoes/', views.listar_submissoes_audesp, name='listar_submissoes_audesp'),
    path('audesp/edital/<int:edital_id>/json/', views.gerar_edital_audesp_json, name='gerar_edital_audesp_json'),
    path('audesp/etp/<int:etp_id>/json/', views.gerar_etp_audesp_json, name='gerar_etp_audesp_json'),
    # -----------------------------------------------------------
    # CRUD e Geração de JSON para: AUDESP Ajustes Contratuais
    # (Representa formalizações, contratos, aditivos para o AUDESP)
    # -----------------------------------------------------------
    path('ajustes-contratuais/criar/', views.criar_ajuste_contratual_audesp, name='criar_ajuste_contratual_audesp'),
    path('ajustes-contratuais/criar/processo/<int:processo_id>/', views.criar_ajuste_contratual_audesp, name='criar_ajuste_contratual_audesp_processo'),
    path('ajustes-contratuais/criar/resultado/<int:resultado_id>/', views.criar_ajuste_contratual_audesp, name='criar_ajuste_contratual_audesp_resultado'),
    path('ajustes-contratuais/<int:pk>/', views.detalhar_ajuste_contratual_audesp, name='detalhar_ajuste_contratual_audesp'),
    path('ajustes-contratuais/<int:pk>/editar/', views.editar_ajuste_contratual_audesp, name='editar_ajuste_contratual_audesp'),
    path('ajuste-contratual-json/<int:ajuste_id>/', views.gerar_ajuste_contratual_audesp_json, name='gerar_ajuste_contratual_audesp_json'),

    # -----------------------------------------------------------
    # CRUD e Geração de JSON para: AUDESP Ata de Registro de Preços
    # (Representa atas de registro de preços para o AUDESP)
    # -----------------------------------------------------------
    path('atas-rp/criar/', views.criar_ata_rp_audesp, name='criar_ata_rp_audesp'), # NOVO: URL de criação
    path('atas-rp/criar/edital/<int:edital_id>/', views.criar_ata_rp_audesp, name='criar_ata_rp_audesp_edital'), # Cria a partir de um Edital
    path('atas-rp/<int:pk>/', views.detalhar_ata_rp_audesp, name='detalhar_ata_rp_audesp'),
    path('atas-rp/<int:pk>/editar/', views.editar_ata_rp_audesp, name='editar_ata_rp_audesp'), # NOVO: URL de edição
    path('ata-rp-json/<int:ata_rp_id>/', views.gerar_ata_rp_audesp_json, name='gerar_ata_rp_audesp_json'),

    # -----------------------------------------------------------
    # CRUD e Geração de JSON para: AUDESP Empenhos de Contrato
    # (Representa empenhos de contrato para o AUDESP)
    # -----------------------------------------------------------
    path('empenhos/criar/', views.criar_empenho_audesp, name='criar_empenho_audesp'), # NOVO: URL de criação
    path('empenhos/criar/ajuste/<int:ajuste_id>/', views.criar_empenho_audesp, name='criar_empenho_audesp_ajuste'), # Cria a partir de um Ajuste Contratual
    path('empenhos/criar/documento-fiscal/<int:df_id>/', views.criar_empenho_audesp, name='criar_empenho_audesp_df'), # Cria a partir de um Doc Fiscal
    path('empenhos/<int:pk>/', views.detalhar_empenho_audesp, name='detalhar_empenho_audesp'),
    path('empenhos/<int:pk>/editar/', views.editar_empenho_audesp, name='editar_empenho_audesp'), # NOVO: URL de edição
    path('empenho-contrato-json/<int:empenho_id>/', views.gerar_empenho_audesp_json, name='gerar_empenho_audesp_json'),

    # -----------------------------------------------------------
    # Geração de JSON para outros tipos (APIs) - Sem CRUD na UI por enquanto
    # -----------------------------------------------------------
    path('edital/enviar-mock/', views.enviar_edital_para_audesp_mock, name='enviar_edital_para_audesp_mock'),

    # Suas URLs de mock de API
    path('mock/login/', views.mock_audesp_login, name='mock_audesp_login'),
    path('mock/enviar/<str:schema_type>/', views.mock_audesp_enviar_pacote, name='mock_audesp_enviar_pacote'),
]
