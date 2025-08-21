# SysGov_Project/core/urls.py

from django.urls import path
from . import views # Para as views normais do core

urlpatterns = [
    # URLs para as páginas principais do core
    path('', views.home_view, name='home'),
    path('meus-processos/', views.meus_processos_view, name='meus_processos'),
    path('processos/novo/', views.criar_processo_view, name='criar_processo'),
    path('processos/<int:processo_id>/', views.detalhes_processo_view, name='detalhes_processo'),

    # URL para adicionar anexos a um processo
    path('processos/<int:processo_id>/anexos/adicionar/', views.adicionar_anexo_ao_processo, name='adicionar_anexo_ao_processo'),

    # <<< ADICIONE ESTAS URLS DE API PARA RENDERIZAR SNIPPETS DE DOCUMENTOS VIA AJAX >>>
    path('api/etp/<int:pk>/render-html/', views.render_etp_detail_snippet, name='api_etp_detail_snippet'),
    path('api/tr/<int:pk>/render-html/', views.render_tr_detail_snippet, name='api_tr_detail_snippet'),
    path('api/edital/<int:pk>/render-html/', views.render_edital_detail_snippet, name='api_edital_detail_snippet'),
    path('api/df/<int:pk>/render-html/', views.render_df_detail_snippet, name='api_df_detail_snippet'),
    path('api/pagamento/<int:pk>/render-html/', views.render_pagamento_detail_snippet, name='api_pagamento_detail_snippet'),
    path('api/arquivo_anexo/<int:pk>/render-html/', views.render_arquivo_anexo_detail_snippet, name='api_arquivo_anexo_detail_snippet'),
    # FIM DA ADIÇÃO <<<
]