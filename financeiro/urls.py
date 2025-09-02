# SysGov_Project/financeiro/urls.py

from django.urls import path
from . import views

app_name = 'financeiro' 

urlpatterns = [
    path('', views.financeiro_dashboard, name='dashboard_financeiro'),

    # URLs para Documentos Fiscais
    path('documentos/registrar/', views.gerar_xml_documento_fiscal, name='registrar_documento_fiscal'),
    path('documentos/registrar/<int:processo_id>/', views.gerar_xml_documento_fiscal, name='registrar_documento_fiscal_processo'),
    path('documentos/', views.listar_documentos_fiscais, name='listar_documentos_fiscais'),
    path('documentos/<int:pk>/', views.detalhar_documento_fiscal, name='detalhar_documento_fiscal'), # <<< ADICIONADO
    path('documentos/<int:pk>/editar/', views.editar_documento_fiscal, name='editar_documento_fiscal'), # <<< ADICIONADO
    path('documentos/<int:pk>/xml/', views.download_df_xml, name='download_df_xml'), # URL para download XML (se não estava)

    # URLs para Pagamentos
    path('pagamentos/registrar/', views.gerar_xml_pagamento, name='registrar_pagamento'),
    path('pagamentos/registrar/<int:processo_id>/', views.gerar_xml_pagamento, name='registrar_pagamento_processo'),
    path('pagamentos/', views.listar_pagamentos, name='listar_pagamentos'),
    path('pagamentos/<int:pk>/', views.detalhar_pagamento, name='detalhar_pagamento'), # <<< ADICIONADO
    path('pagamentos/<int:pk>/editar/', views.editar_pagamento, name='editar_pagamento'), # <<< ADICIONADO
    path('pagamentos/<int:pk>/xml/', views.download_pg_xml, name='download_pg_xml'), # URL para download XML (se não estava)    
    path('audesp/edital/<int:edital_id>/json/', views.gerar_edital_audesp_json, name='gerar_edital_audesp_json'),

    path('contrato/<int:contrato_id>/empenho/criar/', views.criar_empenho, name='criar_empenho'),
    path('empenhos/', views.listar_empenhos, name='listar_empenhos'),
    path('empenho/<int:pk>/', views.detalhar_empenho, name='detalhar_empenho'),
    path('empenho/<int:pk>/editar/', views.editar_empenho, name='editar_empenho')
]
