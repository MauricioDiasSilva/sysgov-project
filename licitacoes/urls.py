# SysGov_Project/sysgov_project/licitacoes/urls.py

from django.urls import path
from . import views


app_name = 'licitacoes' # Essencial

urlpatterns = [
    # Dashboard ou página inicial do módulo de licitações
    path('', views.licitacoes_dashboard, name='dashboard_licitacoes'),

    # URLs para Editais
    path('editais/criar/', views.criar_edital, name='criar_edital'),
    path('editais/criar/<int:processo_id>/', views.criar_edital, name='criar_edital_para_processo'), # Para criar a partir de um Processo
    path('editais/', views.listar_editais, name='listar_editais'),
    path('editais/<int:pk>/', views.detalhar_edital, name='detalhar_edital'),
    path('editais/<int:pk>/editar/', views.editar_edital, name='editar_edital'),
    
    # <<< ADICIONE ESTAS NOVAS URLS PARA RESULTADO DA LICITAÇÃO AQUI
    path('editais/<int:edital_pk>/resultados/registrar/', views.registrar_resultado_licitacao, name='registrar_resultado_licitacao'),
    path('resultados/<int:pk>/', views.detalhar_resultado_licitacao, name='detalhar_resultado_licitacao'),
    path('resultados/', views.listar_resultados_licitacao, name='listar_resultados_licitacao'),
    path('resultados/<int:pk>/editar/', views.editar_resultado_licitacao, name='editar_resultado_licitacao'),
]

