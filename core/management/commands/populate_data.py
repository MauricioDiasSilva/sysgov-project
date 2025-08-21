# # SysGov_Project/core/management/commands/populate_data.py

# import random
# import os
# from datetime import timedelta
# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from faker import Faker
# from django.core.files.base import ContentFile
# from django.conf import settings

# # --- Importe todos os modelos e CHOICES de seus respectivos apps ---
# from core.models import Processo, ArquivoAnexo
# from django.contrib.auth.models import User

# from contratacoes.models import (
#     ETP, TR, PCA, ItemPCA, PesquisaPreco, ParecerTecnico, ModeloTexto, RequisitoPadrao, ItemCatalogo,
#     STATUS_DOCUMENTO_CHOICES as CONTRATACOES_STATUS_DOCUMENTO_CHOICES
# )

# from licitacoes.models import (
#     Edital, Lote, ItemLicitado, ResultadoLicitacao,
#     STATUS_EDITAL_CHOICES as LICITACOES_STATUS_EDITAL_CHOICES,
#     TIPO_INSTRUMENTO_CONVOCATORIO_CHOICES as LICITACOES_TIPO_INSTRUMENTO_CONVOCATORIO_CHOICES,
#     MODALIDADE_LICITACAO_CHOICES as LICITACOES_MODALIDADE_LICITACAO_CHOICES,
#     MODO_DISPUTA_CHOICES, # Corrigido: sem alias
#     VEICULO_PUBLICACAO_CHOICES as LICITACOES_VEICULO_PUBLICACAO_CHOICES,
#     TIPO_BENEFICIO_CHOICES as LICITACOES_TIPO_BENEFICIO_CHOICES,
#     CRITERIO_JULGAMENTO_CHOICES as LICITACOES_CRITERIO_JULGAMENTO_CHOICES,
#     ITEM_CATEGORIA_CHOICES as LICITACOES_ITEM_CATEGORIA_CHOICES
# )

# from financeiro.models import DocumentoFiscal, Pagamento

# from integracao_audesp.models import (
#     AudespConfiguracao, SubmissaoAudesp,
#     AudespAjusteContratual,
#     AudespAtaRegistroPrecos,
#     AudespEmpenhoContrato,
#     AUDESP_TIPO_CONTRATO_CHOICES,
#     AUDESP_CATEGORIA_PROCESSO_CHOICES,
#     AUDESP_TIPO_PESSOA_CHOICES,
#     AUDESP_TIPO_OBJETO_CONTRATO_CHOICES
# )

# from django.contrib.contenttypes.models import ContentType

# class Command(BaseCommand):
#     help = 'Popula o banco de dados com dados fictícios para demonstração do ProGestor Público.'

#     def handle(self, *args, **options):
#         fake = Faker('pt_BR')

#         self.stdout.write(self.style.WARNING('Iniciando a população de dados fictícios para o SysGov...'))

#         try:
#             admin_user = User.objects.get(username='admin')
#         except User.DoesNotExist:
#             self.stdout.write(self.style.ERROR("Usuário 'admin' não encontrado. Por favor, crie um superusuário primeiro ('python manage.py createsuperuser')."))
#             return

#         self.stdout.write(self.style.WARNING('Deletando dados antigos de todos os modelos...'))
#         SubmissaoAudesp.objects.all().delete()
#         AudespEmpenhoContrato.objects.all().delete()
#         AudespAtaRegistroPrecos.objects.all().delete()
#         AudespAjusteContratual.objects.all().delete()
#         DocumentoFiscal.objects.all().delete()
#         Pagamento.objects.all().delete()
#         ResultadoLicitacao.objects.all().delete()
#         ItemLicitado.objects.all().delete()
#         Lote.objects.all().delete()
#         Edital.objects.all().delete()
#         ParecerTecnico.objects.all().delete()
#         PesquisaPreco.objects.all().delete()
#         ETP.objects.all().delete()
#         TR.objects.all().delete()
#         ItemPCA.objects.all().delete()
#         PCA.objects.all().delete()
#         Processo.objects.all().delete()
#         ArquivoAnexo.objects.all().delete()
#         AudespConfiguracao.objects.all().delete()
#         ItemCatalogo.objects.all().delete()
#         ModeloTexto.objects.all().delete()
#         RequisitoPadrao.objects.all().delete()
#         self.stdout.write(self.style.SUCCESS('Dados antigos deletados com sucesso.'))

#         audesp_config, created = AudespConfiguracao.objects.get_or_create(
#             municipio_codigo_audesp=random.choice([7107, 7050]),
#             entidade_codigo_audesp=random.choice([10048, 20050]),
#             defaults={}
#         )
#         self.stdout.write(f'  Configuração AUDESP {"criada" if created else "obtida"}: {audesp_config}')

#         pcas = []
#         pca_current_year, created_pca_cy = PCA.objects.get_or_create(
#             ano_vigencia=timezone.now().year,
#             defaults={'data_aprovacao': fake.date_this_year(), 'responsavel_aprovacao': admin_user, 'titulo': f'PCA {timezone.now().year} - Planejamento Geral'}
#         )
#         pcas.append(pca_current_year)
#         pca_next_year, created_pca_ny = PCA.objects.get_or_create(
#             ano_vigencia=timezone.now().year + 1,
#             defaults={'data_aprovacao': fake.date_this_year(), 'responsavel_aprovacao': admin_user, 'titulo': f'PCA {timezone.now().year + 1} - Planejamento Futuro'}
#         )
#         pcas.append(pca_next_year)
#         for pca in pcas:
#             for j in range(random.randint(5, 10)):
#                 ItemPCA.objects.create(
#                     pca=pca, identificador_item=f'ITEM-{pca.ano_vigencia}-{j+1:03d}-{fake.random_int(min=100, max=999)}',
#                     descricao_item=fake.sentence(nb_words=8), valor_estimado_pca=random.uniform(5000.00, 500000.00),
#                     unidade_requisitante=fake.company_suffix().upper(),
#                 )
#         if not ItemPCA.objects.exists():
#             self.stdout.write(self.style.ERROR("Nenhum ItemPCA gerado. Verifique a lógica de criação de PCA e ItemPCA."))
#             return
#         self.stdout.write(self.style.SUCCESS(f'Gerados {ItemPCA.objects.count()} Itens PCA no total.'))

#         for _ in range(10):
#             ItemCatalogo.objects.create(
#                 nome_padronizado=fake.unique.word().capitalize() + ' ' + fake.unique.word().capitalize() + ' ' + fake.unique.word().capitalize(),
#                 descricao_tecnica=fake.paragraph(nb_sentences=3),
#                 unidade_medida=random.choice(['UN', 'KG', 'M', 'L', 'PCT', 'CX', 'SERVICO']),
#                 preco_historico_medio=random.uniform(10.00, 5000.00),
#             )
#         self.stdout.write(self.style.SUCCESS(f'Gerados {ItemCatalogo.objects.count()} Itens de Catálogo.'))

#         ModeloTexto.objects.create(titulo="Modelo de Justificativa Padrão", texto=fake.paragraph(nb_sentences=10))
#         ModeloTexto.objects.create(titulo="Modelo de Objeto de Contratação", texto=fake.paragraph(nb_sentences=8))
#         self.stdout.write(self.style.SUCCESS(f'Gerados {ModeloTexto.objects.count()} Modelos de Texto.'))

#         for _ in range(7):
#             RequisitoPadrao.objects.create(
#                 codigo=fake.unique.bothify(text='REQ-###'), titulo=fake.sentence(nb_words=4),
#                 descricao=fake.paragraph(nb_sentences=2), ativo=random.choice([True, False])
#             )
#         self.stdout.write(self.style.SUCCESS(f'Gerados {RequisitoPadrao.objects.count()} Requisitos Padrão.'))


#         # --- Gerar Processos Completos (com ETP, TR, Edital, DF, Pagamento) ---
#         num_processos_completos_aleatorios = 15 # Renomeado para clareza
#         self.stdout.write(self.style.WARNING(f'Gerando {num_processos_completos_aleatorios} processos completos aleatórios...'))

#         # --- Processo Forçado para garantir AudespAjusteContratual, Ata RP e Empenho ---
#         self.stdout.write(self.style.WARNING('\nGerando um processo FORÇADO para garantir dados AUDESP...'))
#         processo_forced = Processo.objects.create(
#             usuario=admin_user, titulo="Processo AUDESP Forçado para Testes Completos",
#             descricao="Processo para garantir a criação de AudespAjusteContratual, Ata RP e Empenho.",
#             numero_protocolo=f'{timezone.now().year}/FORCED-PMB-TESTE-{fake.random_int(min=100, max=999):03d}', # Mais exclusivo
#             status='CONCLUIDO'
#         )
#         etp_forced = ETP.objects.create(
#             processo_vinculado=processo_forced, titulo="ETP Forçado para Testes AUDESP",
#             numero_processo=f'{processo_forced.numero_protocolo}-ETP', setor_demandante=fake.company_suffix(),
#             autor=admin_user, estimativa_valor=random.uniform(150000.00, 800000.00), status='APROVADO',
#             item_pca_vinculado=random.choice(ItemPCA.objects.all()), descricao_necessidade=fake.paragraph(),
#             objetivo_contratacao=fake.sentence(), requisitos_contratacao=fake.paragraph(),
#             levantamento_solucoes_mercado=fake.paragraph(), estimativa_quantidades='100 unidades',
#             resultados_esperados=fake.paragraph(), viabilidade_justificativa_solucao=fake.paragraph(),
#             alinhamento_planejamento=fake.paragraph()
#         )
#         tr_forced = TR.objects.create(
#             processo_vinculado=processo_forced, etp_origem=etp_forced, titulo="TR Forçado para Testes AUDESP",
#             numero_processo=f'{processo_forced.numero_protocolo}-TR', data_criacao=fake.date_this_month(),
#             autor=admin_user, objeto=fake.paragraph(), justificativa=fake.paragraph(),
#             especificacoes_tecnicas=fake.paragraph(), prazo_execucao_entrega='60 dias',
#             estimativa_preco_tr=etp_forced.estimativa_valor * random.uniform(0.9, 0.95), status='APROVADO'
#         )
#         edital_forced = Edital.objects.create(
#             processo_vinculado=processo_forced, numero_edital=f'ED-FORCED-{timezone.now().year}-{fake.random_int(min=10, max=99):02d}',
#             titulo="Edital Forçado para Testes AUDESP", tipo_licitacao='PREGAO_ELETRONICO',
#             data_publicacao=fake.date_this_month(), data_abertura_propostas=fake.date_time_this_month(before_now=False, after_now=True),
#             valor_estimado=tr_forced.estimativa_preco_tr, status='HOMOLOGADO', responsavel_publicacao=admin_user,
#             link_edital_completo=fake.url(), retificacao=False,
#             codigo_unidade_compradora=fake.bothify(text='UC###'),
#             tipo_instrumento_convocatorio_audesp=random.choice([c[0] for c in LICITACOES_TIPO_INSTRUMENTO_CONVOCATORIO_CHOICES]),
#             modalidade_audesp=random.choice([c[0] for c in LICITACOES_MODALIDADE_LICITACAO_CHOICES]),
#             modo_disputa=random.choice([c[0] for c in MODO_DISPUTA_CHOICES]), # Corrigido
#             numero_compra_audesp=fake.bothify(text='COMPRA-####-###'), ano_compra_audesp=timezone.now().year,
#             numero_processo_origem_audesp=processo_forced.numero_protocolo, objeto_compra_audesp=fake.paragraph(),
#             data_encerramento_proposta=fake.date_time_this_month(before_now=False, after_now=True),
#             amparo_legal=random.choice([i for i in range(1, 1021)]), link_sistema_origem=fake.url(),
#         )
#         resultado_forced = ResultadoLicitacao.objects.create(
#             edital=edital_forced, fornecedor_vencedor=fake.company(), cnpj_vencedor=fake.cnpj(),
#             valor_homologado=edital_forced.valor_estimado * random.uniform(0.9, 0.99), data_homologacao=fake.date_this_month(),
#             responsavel_registro=admin_user, valor_estimado_inicial=edital_forced.valor_estimado
#         )
#         self.stdout.write('  Processo FORÇADO (Edital HOMOLOGADO e Resultado) criado.')

#         if not ItemLicitado.objects.filter(edital=edital_forced).exists():
#             lote_dummy = Lote.objects.create(edital=edital_forced, numero_lote='1', descricao='Lote Único', valor_estimado_lote=edital_forced.valor_estimado)
#             ItemLicitado.objects.create(
#                 lote=lote_dummy, descricao_item='Item Forçado 1', quantidade=10, unidade_medida='UN', valor_referencia=100.00,
#                 numero_item_audesp=1, material_ou_servico='M', tipo_beneficio=1, incentivo_produtivo_basico=False,
#                 orcamento_sigiloso=False, valor_unitario_estimado_audesp=90.0000, valor_total_audesp=900.0000,
#                 criterio_julgamento=1, item_categoria=3
#             )
#         self.stdout.write('  Itens Licitados FORÇADOS criados para o Edital forçado.')


#         itens_contratados_ids_ajuste = list(ItemLicitado.objects.filter(lote__edital=edital_forced).values_list('pk', flat=True))
#         despesas_dummy = [fake.bothify(text='#########') for _ in range(random.randint(1,2))]
#         fonte_recursos_dummy = [random.choice([1, 8, 91, 92])]

#         audesp_ajuste_forced = AudespAjusteContratual.objects.create(
#             processo_vinculado=processo_forced, resultado_licitacao_origem=resultado_forced, edital_origem=edital_forced,
#             adesao_participacao=True, gerenciadora_jurisdicionada=True, cnpj_gerenciadora=fake.cnpj(),
#             municipio_gerenciador=audesp_config.municipio_codigo_audesp, entidade_gerenciadora=audesp_config.entidade_codigo_audesp,
#             codigo_edital_audesp=edital_forced.numero_edital,
#             codigo_ata_rp_audesp=f'ATA-RP-FORCED-{timezone.now().year}-{fake.random_int(min=100, max=999):03d}',
#             codigo_contrato_audesp=f'AJUSTE-FORCED-{timezone.now().year}-{fake.random_int(min=1000, max=9999):04d}', retificacao=False,
#             fonte_recursos_contratacao=fonte_recursos_dummy, itens_contratados_ids=itens_contratados_ids_ajuste,
#             tipo_contrato_id=random.choice([c[0] for c in AUDESP_TIPO_CONTRATO_CHOICES]),
#             numero_contrato_empenho=edital_forced.numero_edital, ano_contrato=timezone.now().year,
#             processo_sistema_origem=processo_forced.numero_protocolo, categoria_processo_id=random.choice([c[0] for c in AUDESP_CATEGORIA_PROCESSO_CHOICES]),
#             receita=False, despesas_classificacao=despesas_dummy,
#             codigo_unidade=fake.bothify(text='PNCP-UNI-##'), ni_fornecedor=resultado_forced.cnpj_vencedor,
#             tipo_pessoa_fornecedor=random.choice([c[0] for c in AUDESP_TIPO_PESSOA_CHOICES]), nome_razao_social_fornecedor=resultado_forced.fornecedor_vencedor,
#             ni_fornecedor_subcontratado=fake.cnpj() if random.random() > 0.8 else None,
#             tipo_pessoa_fornecedor_subcontratado=random.choice([c[0] for c in AUDESP_TIPO_PESSOA_CHOICES]) if random.random() > 0.8 else None,
#             nome_razao_social_fornecedor_subcontratado=fake.company() if random.random() > 0.8 else None,
#             objeto_contrato=fake.paragraph(nb_sentences=4), informacao_complementar=fake.paragraph(nb_sentences=2) if random.random() > 0.5 else None,
#             valor_inicial=float(resultado_forced.valor_homologado), numero_parcelas=random.randint(1, 12),
#             valor_parcela=random.uniform(100, 10000), valor_global=float(resultado_forced.valor_homologado),
#             valor_acumulado=random.uniform(1000, 50000), data_assinatura=fake.date_this_month(),
#             data_vigencia_inicio=fake.date_this_month(after_today=True), data_vigencia_fim=fake.future_date(end_date='+3y'),
#             vigencia_meses=random.randint(1, 36), tipo_objeto_contrato=random.choice([c[0] for c in AUDESP_TIPO_OBJETO_CONTRATO_CHOICES]), # <<< AQUI
#             criado_por=admin_user,
#         )
#         self.stdout.write(f'  AudespAjusteContratual FORÇADO criado: {audesp_ajuste_forced.codigo_contrato_audesp}')

#         # --- Gerar AudespAtaRegistroPrecos para o processo forçado ---
#         itens_licitados_ids_ata = list(ItemLicitado.objects.filter(edital=edital_forced).values_list('pk', flat=True))
#         ata_rp_forced = AudespAtaRegistroPrecos.objects.create(
#             processo_vinculado=processo_forced, edital_origem=edital_forced,
#             municipio=audesp_config.municipio_codigo_audesp, entidade=audesp_config.entidade_codigo_audesp,
#             codigo_edital_audesp=edital_forced.numero_edital,
#             codigo_ata_audesp=f'ATA-RP-{timezone.now().year}-{random.randint(100, 999):03d}', ano_compra=timezone.now().year,
#             retificacao=False, itens_licitados_ids=itens_licitados_ids_ata,
#             numero_ata_registro_preco=f'ARP-{timezone.now().year}-{random.randint(1000, 9999):04d}', ano_ata=timezone.now().year,
#             data_assinatura=fake.date_this_month(), data_vigencia_inicio=fake.date_this_month(after_today=True),
#             data_vigencia_fim=fake.future_date(end_date='+2y'),
#             criado_por=admin_user,
#             # Campos do AudespAtaRegistroPrecos que estavam faltando ou eram opcionais
#             # Adicione aqui para garantir que são preenchidos
#             # exemplo: tipo_objeto_contrato=random.choice([c[0] for c in AUDESP_TIPO_OBJETO_CONTRATO_CHOICES]),
#             # mas este modelo nao tem este campo
#         )
#         self.stdout.write(f'  AudespAtaRegistroPrecos FORÇADO criado: {ata_rp_forced.codigo_ata_audesp}')

#         # --- Gerar AudespEmpenhoContrato para o processo forçado ---
#         df_forced = DocumentoFiscal.objects.create(
#             processo_vinculado=processo_forced, codigo_ajuste=f'AJ-FORCE-{fake.random_int(min=10, max=99):02d}',
#             medicao_numero=1, nota_empenho_numero=f'EMP-FORCE-{fake.random_int(min=1000, max=9999):04d}',
#             nota_empenho_data_emissao=fake.date_this_month(), documento_fiscal_numero=f'NF-FORCE-{fake.random_int(min=100000, max=999999)}',
#             documento_fiscal_uf=fake.state_abbr(), documento_fiscal_valor=float(resultado_forced.valor_homologado),
#             documento_fiscal_data_emissao=fake.date_this_month(),
#         )
#         empenho_forced = AudespEmpenhoContrato.objects.create(
#             ajuste_contratual_audesp=audesp_ajuste_forced, documento_fiscal_origem=df_forced, processo_vinculado=processo_forced,
#             municipio=audesp_config.municipio_codigo_audesp, entidade=audesp_config.entidade_codigo_audesp,
#             codigo_contrato_audesp=audesp_ajuste_forced.codigo_contrato_audesp, retificacao=False,
#             numero_empenho=f'EMP-FORCED-{timezone.now().year}-{fake.random_int(min=10000, max=99999):05d}', ano_empenho=timezone.now().year,
#             data_emissao_empenho=fake.date_this_month(), criado_por=admin_user,
#             # Campos do AudespEmpenhoContrato que estavam faltando ou eram opcionais
#             # exemplo: tipo_objeto_contrato=random.choice([c[0] for c in AUDESP_TIPO_OBJETO_CONTRATO_CHOICES]),
#             # este modelo também não tem este campo.
#         )
#         self.stdout.write(f'  AudespEmpenhoContrato FORÇADO criado: {empenho_forced.numero_empenho}')


# # ... (restante do populate_data.py)


#         self.stdout.write(self.style.WARNING('\nGerando processos aleatórios adicionais...'))
#         for i in range(num_processos_completos_aleatorios): # Loop para gerar processos aleatórios adicionais
#             processo = Processo.objects.create(
#                 usuario=admin_user, titulo=fake.sentence(nb_words=6),
#                 descricao=fake.paragraph(nb_sentences=3),
#                 numero_protocolo=f'{timezone.now().year}/{random.randint(1000, 9999):04d}-PMB-{i+10}',
#                 status=random.choice([s[0] for s in Processo.STATUS_CHOICES])
#             )
#             self.stdout.write(f'\nProcesso Criado: {processo.numero_protocolo} - "{processo.titulo}"')

#             etp_status = random.choice([s[0] for s in CONTRATACOES_STATUS_DOCUMENTO_CHOICES])
#             etp = ETP.objects.create(
#                 processo_vinculado=processo, titulo=f'ETP - {processo.titulo}',
#                 numero_processo=f'{processo.numero_protocolo}-ETP', setor_demandante=fake.company_suffix(),
#                 autor=admin_user, descricao_necessidade=fake.paragraph(nb_sentences=5),
#                 objetivo_contratacao=fake.sentence(), requisitos_contratacao=fake.paragraph(nb_sentences=4),
#                 levantamento_solucoes_mercado=fake.paragraph(nb_sentences=5), estimativa_quantidades=f'{random.randint(1, 100)} {fake.word()}',
#                 estimativa_valor=random.uniform(10000.00, 1000000.00), resultados_esperados=fake.paragraph(nb_sentences=3),
#                 viabilidade_justificativa_solucao=fake.paragraph(nb_sentences=4), alinhamento_planejamento=fake.paragraph(nb_sentences=2),
#                 status=etp_status, item_pca_vinculado=random.choice(ItemPCA.objects.all())
#             )
#             self.stdout.write(f'  - ETP Criado (Status: {etp.get_status_display()})')
            
#             num_pesquisas = random.randint(3, 5)
#             for _ in range(num_pesquisas):
#                 PesquisaPreco.objects.create(
#                     etp=etp,
#                     fornecedor=fake.company(),
#                     valor_cotado=random.uniform(float(etp.estimativa_valor) * 0.8, float(etp.estimativa_valor) * 1.2),
#                     data_pesquisa=fake.date_this_year(),
#                 )
#             self.stdout.write(f'    - {num_pesquisas} Pesquisas de Preço adicionadas ao ETP.')

#             if random.random() > 0.5:
#                 ParecerTecnico.objects.create(etp=etp, conteudo=fake.paragraph(nb_sentences=7), autor=admin_user)
#                 self.stdout.write('    - Parecer Técnico adicionado ao ETP.')
#             if random.random() > 0.6:
#                 anexo_etp = ArquivoAnexo.objects.create(titulo=f'Anexo ETP {etp.pk} - {fake.word().capitalize()} Relatório.pdf', uploaded_by=admin_user, content_object=etp)
#                 etp.anexos.add(anexo_etp)
#                 self.stdout.write(f'    - Anexo genérico criado e vinculado ao ETP.')

#             tr = None
#             if etp_status in ['APROVADO', 'REVISADO']:
#                 tr_status = random.choice([s[0] for s in CONTRATACOES_STATUS_DOCUMENTO_CHOICES])
#                 tr = TR.objects.create(
#                     processo_vinculado=processo, etp_origem=etp, titulo=f'TR - {processo.titulo}',
#                     numero_processo=f'{processo.numero_protocolo}-TR-{i+1}', data_criacao=fake.date_this_month(),
#                     autor=admin_user, objeto=fake.paragraph(nb_sentences=4), justificativa=fake.paragraph(nb_sentences=3),
#                     especificacoes_tecnicas=fake.paragraph(nb_sentences=5), prazo_execucao_entrega='30 dias úteis',
#                     estimativa_preco_tr=etp.estimativa_valor * random.uniform(0.9, 1.1), status=tr_status
#                 )
#                 self.stdout.write(f'  - TR Criado (Status: {tr.get_status_display()})')
#                 if random.random() > 0.6:
#                     anexo_tr = ArquivoAnexo.objects.create(titulo=f'Anexo TR {tr.pk} - {fake.word().capitalize()} Parecer.pdf', uploaded_by=admin_user, content_object=tr)
#                     tr.anexos.add(anexo_tr)
#                     self.stdout.write(f'    - Anexo genérico criado e vinculado ao TR.')

#             eedital = None # Zera a variável edital para cada iteração
#             # Só cria Edital se TR foi aprovado/revisado
#             if tr and tr_status in ['APROVADO', 'REVISADO']:
#                 edital_status = random.choice([s[0] for s in LICITACOES_STATUS_EDITAL_CHOICES])
#                 edital = Edital.objects.create(
#                     processo_vinculado=processo, # <<< AGORA USA 'processo' DESTA ITERAÇÃO DO LOOP
#                     numero_edital=f'ED-{timezone.now().year}-{random.randint(100, 999):03d}-{i+100}', # <<< AUMENTEI O RANGE PARA GARANTIR UNICIDADE GLOBAL
#                     titulo=f'Edital - {processo.titulo}',
#                     tipo_licitacao=random.choice(['PREGAO_ELETRONICO', 'CONCORRENCIA', 'TOMADA_PRECOS']),
#                     data_publicacao=fake.date_this_month(),
#                     data_abertura_propostas=fake.date_time_this_month(before_now=False, after_now=True),
#                     valor_estimado=tr.estimativa_preco_tr,
#                     status=edital_status,
#                     responsavel_publicacao=admin_user,
#                     link_edital_completo=fake.url(),
#                     retificacao=random.choice([True, False]),
#                     codigo_unidade_compradora=fake.bothify(text='UC###'),
#                     tipo_instrumento_convocatorio_audesp=random.choice([c[0] for c in LICITACOES_TIPO_INSTRUMENTO_CONVOCATORIO_CHOICES]),
#                     modalidade_audesp=random.choice([c[0] for c in LICITACOES_MODALIDADE_LICITACAO_CHOICES]),
#                     modo_disputa=random.choice([c[0] for c in MODO_DISPUTA_CHOICES]),
#                     numero_compra_audesp=fake.bothify(text='COMPRA-####-###'),
#                     ano_compra_audesp=timezone.now().year,
#                     numero_processo_origem_audesp=processo.numero_protocolo,
#                     objeto_compra_audesp=f'Objeto do Edital {edital.numero_edital}' if edital and hasattr(edital, 'numero_edital') else fake.paragraph(),
#                     informacao_complementar=fake.paragraph(nb_sentences=2) if random.random() > 0.3 else None,
#                     srp=random.choice([True, False]),
#                     data_encerramento_proposta=fake.date_time_this_month(before_now=False, after_now=True),
#                     amparo_legal=random.choice([i for i in range(1, 1021)]),
#                     link_sistema_origem=fake.url() if random.random() > 0.3 else None,
#                     justificativa_presencial=fake.paragraph(nb_sentences=1) if random.random() > 0.5 else None,
#                 )
#                 self.stdout.write(f'  - Edital Criado (Status: {edital.get_status_display()})')


#                 num_lotes = random.randint(1, 3)
#                 for k in range(num_lotes):
#                     lote = Lote.objects.create(
#                         edital=edital, numero_lote=f'{k+1}', descricao=fake.sentence(nb_words=5),
#                         valor_estimado_lote=random.uniform(float(edital.valor_estimado) * 0.1, float(edital.valor_estimado) * 0.5)
#                     )
#                     num_itens = random.randint(1, 4)
#                     for l in range(num_itens):
#                         ItemLicitado.objects.create(
#                             lote=lote, descricao_item=fake.word().capitalize() + ' ' + fake.color_name() + ' ' + fake.word(),
#                             quantidade=random.randint(1, 100), unidade_medida=random.choice(['UN', 'KG', 'PCT', 'METRO']),
#                             valor_referencia=random.uniform(10.00, 1000.00), numero_item_audesp=l+1,
#                             material_ou_servico=random.choice(['M', 'S']), tipo_beneficio=random.choice([c[0] for c in LICITACOES_TIPO_BENEFICIO_CHOICES]),
#                             incentivo_produtivo_basico=random.choice([True, False]), orcamento_sigiloso=random.choice([True, False]),
#                             valor_unitario_estimado_audesp=random.uniform(10.0000, 1000.0000), valor_total_audesp=random.uniform(100.0000, 5000.0000),
#                             criterio_julgamento=random.choice([c[0] for c in LICITACOES_CRITERIO_JULGAMENTO_CHOICES]),
#                             item_categoria=random.choice([c[0] for c in LICITACOES_ITEM_CATEGORIA_CHOICES]),
#                             patrimonio=fake.unique.bothify(text='PAT-#####') if random.random() > 0.7 else None,
#                             codigo_registro_imobiliario=fake.unique.bothify(text='IMO-#####') if random.random() > 0.7 else None,
#                         )
#                 self.stdout.write(f'    - {num_lotes} Lotes e {ItemLicitado.objects.filter(lote__edital=edital).count()} itens adicionados ao Edital.')

#                 resultado = None
#                 if edital_status in ['PUBLICADO', 'ABERTO', 'ENCERRADO']:
#                     if random.random() > 0.4:
#                         valor_homologado_base = float(edital.valor_estimado) * random.uniform(0.7, 0.95)
#                         resultado = ResultadoLicitacao.objects.create(
#                             edital=edital, fornecedor_vencedor=fake.company(), cnpj_vencedor=fake.cnpj(),
#                             valor_homologado=valor_homologado_base, data_homologacao=fake.date_this_month(),
#                             responsavel_registro=admin_user, valor_estimado_inicial=edital.valor_estimado
#                         )
#                         edital.status = 'HOMOLOGADO'
#                         edital.save()
#                         self.stdout.write(f'  - Resultado da Licitação Registrado (Vencedor: {resultado.fornecedor_vencedor})')
#                     else:
#                         if edital_status in ['PUBLICADO', 'ABERTO']:
#                             edital.status = random.choice(['CANCELADO', 'FRACASSADO'])
#                             edital.save()
#                             self.stdout.write(f'  - Edital Finalizado Sem Resultado (Status: {edital.get_status_display()})')

#                 df = None
#                 if edital and edital.status == 'HOMOLOGADO' and resultado:
#                     df_valor = float(resultado.valor_homologado) * random.uniform(0.95, 1.05)
#                     df = DocumentoFiscal.objects.create(
#                         processo_vinculado=processo, codigo_ajuste=f'AJ-{processo.numero_protocolo.split("/")[0]}-{random.randint(10, 99):02d}',
#                         medicao_numero=1, nota_empenho_numero=f'EMP-{timezone.now().year}-{random.randint(1000, 9999):04d}',
#                         nota_empenho_data_emissao=fake.date_this_month(), documento_fiscal_numero=f'NF-{random.randint(100000, 999999)}',
#                         documento_fiscal_uf=fake.state_abbr(), documento_fiscal_valor=df_valor,
#                         documento_fiscal_data_emissao=fake.date_this_month(),
#                     )
#                     self.stdout.write(f'  - Documento Fiscal Criado (NF: {df.documento_fiscal_numero})')

#                     if random.random() > 0.3:
#                         Pagamento.objects.create(
#                             processo_vinculado=processo, codigo_ajuste=df.codigo_ajuste,
#                             medicao_numero=df.medicao_numero, nota_empenho_numero=df.nota_empenho_numero,
#                             nota_empenho_data_emissao=df.nota_empenho_data_emissao,
#                             documento_fiscal_numero=df.documento_fiscal_numero,
#                             documento_fiscal_data_emissao=df.documento_fiscal_data_emissao,
#                             documento_fiscal_uf=df.documento_fiscal_uf,
#                             nota_fiscal_valor_pago=df.documento_fiscal_valor,
#                             nota_fiscal_pagto_dt=fake.date_this_month(after_today=True, before_today=False),
#                             recolhido_encargos_previdenciario=random.choice(['S', 'N']),
#                         )
#                         self.stdout.write(f'  - Pagamento Registrado (NF: {df.documento_fiscal_numero})')

#                 # --- Gerar AudespAjusteContratual (suas "atas" do AUDESP) ---
#                 audesp_ajuste = None
#                 # Força a criação se é o primeiro processo ou se as condições são atendidas
#                 if resultado and edital.status == 'HOMOLOGADO' or i == 0:
#                     if i == 0 and not (resultado and edital.status == 'HOMOLOGADO'):
#                         # Se é o primeiro loop e as condições não foram atendidas, força a criação do processo completo para ajuste
#                         self.stdout.write(self.style.WARNING("    Forçando criação de AudespAjusteContratual para o primeiro processo..."))
#                         processo_forced = Processo.objects.create(
#                             usuario=admin_user, titulo="Processo Forçado para Ajuste Contratual AUDESP",
#                             descricao="Processo para garantir dados de AudespAjusteContratual",
#                             numero_protocolo=f'{timezone.now().year}/FORCED-PMB-AJUSTE', status='CONCLUIDO'
#                         )
#                         etp_forced = ETP.objects.create(
#                             processo_vinculado=processo_forced, titulo="ETP Forçado para Testes AUDESP",
#                             numero_processo=f'{processo_forced.numero_protocolo}-ETP', setor_demandante=fake.company_suffix(),
#                             autor=admin_user, estimativa_valor=random.uniform(150000.00, 800000.00), status='APROVADO',
#                             item_pca_vinculado=random.choice(ItemPCA.objects.all()), descricao_necessidade=fake.paragraph(),
#                             objetivo_contratacao=fake.sentence(), requisitos_contratacao=fake.paragraph(),
#                             levantamento_solucoes_mercado=fake.paragraph(), estimativa_quantidades='100 unidades',
#                             resultados_esperados=fake.paragraph(), viabilidade_justificativa_solucao=fake.paragraph(),
#                             alinhamento_planejamento=fake.paragraph()
#                         )
#                         tr_forced = TR.objects.create(
#                             processo_vinculado=processo_forced, etp_origem=etp_forced, titulo="TR Forçado",
#                             numero_processo=f'{processo_forced.numero_protocolo}-TR-FORCE', data_criacao=fake.date_this_month(),
#                             autor=admin_user, objeto=fake.paragraph(), justificativa=fake.paragraph(),
#                             especificacoes_tecnicas=fake.paragraph(), prazo_execucao_entrega='60 dias',
#                             estimativa_preco_tr=etp_forced.estimativa_valor * random.uniform(0.9, 0.95), status='APROVADO'
#                         )
#                         edital_forced = Edital.objects.create(
#                             processo_vinculado=processo_forced, numero_edital=f'ED-FORCE-AJUSTE-{timezone.now().year}-{random.randint(1, 999):03d}',
#                             titulo="Edital Forçado para Ajuste", tipo_licitacao='PREGAO_ELETRONICO',
#                             data_publicacao=fake.date_this_month(), data_abertura_propostas=fake.date_time_this_month(before_now=False, after_now=True),
#                             valor_estimado=90000.00, status='HOMOLOGADO', responsavel_publicacao=admin_user,
#                             link_edital_completo=fake.url(), retificacao=False,
#                             codigo_unidade_compradora=fake.bothify(text='UC###'),
#                             tipo_instrumento_convocatorio_audesp=random.choice([c[0] for c in LICITACOES_TIPO_INSTRUMENTO_CONVOCATORIO_CHOICES]),
#                             modalidade_audesp=random.choice([c[0] for c in LICITACOES_MODALIDADE_LICITACAO_CHOICES]),
#                             modo_disputa=random.choice([c[0] for c in MODO_DISPUTA_CHOICES]),
#                             numero_compra_audesp=fake.bothify(text='COMPRA-####-###'), ano_compra_audesp=timezone.now().year,
#                             numero_processo_origem_audesp=processo_forced.numero_protocolo, objeto_compra_audesp=fake.paragraph(),
#                             data_encerramento_proposta=fake.date_time_this_month(before_now=False, after_now=True),
#                             amparo_legal=random.choice([i for i in range(1, 1021)]), link_sistema_origem=fake.url(),
#                         )
#                         resultado_forced = ResultadoLicitacao.objects.create(
#                             edital=edital_forced, fornecedor_vencedor=fake.company(), cnpj_vencedor=fake.cnpj(),
#                             valor_homologado=85000.00, data_homologacao=fake.date_this_month(),
#                             responsavel_registro=admin_user, valor_estimado_inicial=edital_forced.valor_estimado
#                         )
#                         processo_ajuste = processo_forced
#                         resultado_ajuste = resultado_forced
#                         edital_ajuste = edital_forced
#                         self.stdout.write(self.style.WARNING("    Processo, Edital e Resultado forçados (Ajuste) criados com sucesso!"))
#                     else:
#                         processo_ajuste = processo
#                         resultado_ajuste = resultado
#                         edital_ajuste = edital

#                     itens_contratados_ids = list(ItemLicitado.objects.filter(lote__edital=edital_ajuste).values_list('pk', flat=True))
#                     if not itens_contratados_ids and edital_ajuste: # Garante itens para edital forçado ou com falha
#                          lote_dummy = Lote.objects.create(edital=edital_ajuste, numero_lote='100-D', descricao='Lote Dummy para Ajuste', valor_estimado_lote=100.00)
#                          item_dummy = ItemLicitado.objects.create(lote=lote_dummy, descricao_item='Item Dummy Ajuste', quantidade=1, unidade_medida='UN', valor_referencia=10.00, numero_item_audesp=1, material_ou_servico='M', tipo_beneficio=1, orcamento_sigiloso=False, valor_unitario_estimado_audesp=10.00, valor_total_audesp=10.00, criterio_julgamento=1, item_categoria=1)
#                          itens_contratados_ids.append(item_dummy.pk)


#                     despesas_dummy = [fake.bothify(text='#########') for _ in range(random.randint(1,2))]
#                     fonte_recursos_dummy = [random.choice([1, 8, 91, 92])]

#                     audesp_ajuste = AudespAjusteContratual.objects.create(
#                         processo_vinculado=processo_ajuste,
#                         resultado_licitacao_origem=resultado_ajuste,
#                         edital_origem=edital_ajuste, # Referência ao Edital
#                         # Campos do descritor
#                         adesao_participacao=random.choice([True, False]),
#                         gerenciadora_jurisdicionada=random.choice([True, False]) if random.random() > 0.5 else None,
#                         cnpj_gerenciadora=fake.cnpj() if random.random() > 0.5 else None,
#                         municipio_gerenciador=random.randint(1, 9999) if random.random() > 0.5 else None,
#                         entidade_gerenciadora=random.randint(1, 99999) if random.random() > 0.5 else None,
#                         codigo_edital_audesp=edital_ajuste.numero_edital,
#                         codigo_ata_rp_audesp=f'ATA-{timezone.now().year}-{random.randint(100, 999):03d}',
#                         codigo_contrato_audesp=f'AJUSTE-{timezone.now().year}-{random.randint(1000, 9999):04d}', retificacao=random.choice([True, False]),

#                         # Campos principais do ajuste
#                         fonte_recursos_contratacao=fonte_recursos_dummy,
#                         itens_contratados_ids=itens_contratados_ids,
#                         tipo_contrato_id=random.choice([c[0] for c in AUDESP_TIPO_CONTRATO_CHOICES]),
#                         numero_contrato_empenho=edital_ajuste.numero_edital, ano_contrato=timezone.now().year,
#                         processo_sistema_origem=processo_ajuste.numero_protocolo, categoria_processo_id=random.choice([c[0] for c in AUDESP_CATEGORIA_PROCESSO_CHOICES]),
#                         receita=random.choice([True, False]),
#                         despesas_classificacao=[fake.bothify(text='#########') for _ in range(random.randint(1,2))],
#                         codigo_unidade=fake.bothify(text='PNCP-UNI-##'),
#                         ni_fornecedor=resultado_ajuste.cnpj_vencedor,
#                         tipo_pessoa_fornecedor=random.choice([c[0] for c in AUDESP_TIPO_PESSOA_CHOICES]), nome_razao_social_fornecedor=resultado_ajuste.fornecedor_vencedor,
#                         ni_fornecedor_subcontratado=fake.cnpj() if random.random() > 0.8 else None,
#                         tipo_pessoa_fornecedor_subcontratado=random.choice([c[0] for c in AUDESP_TIPO_PESSOA_CHOICES]) if random.random() > 0.8 else None,
#                         nome_razao_social_fornecedor_subcontratado=fake.company() if random.random() > 0.8 else None,
#                         objeto_contrato=fake.paragraph(nb_sentences=4), informacao_complementar=fake.paragraph(nb_sentences=2) if random.random() > 0.5 else None,
#                         valor_inicial=float(resultado_ajuste.valor_homologado), numero_parcelas=random.randint(1, 12),
#                         valor_parcela=random.uniform(100, 10000), valor_global=float(resultado_ajuste.valor_homologado),
#                         valor_acumulado=random.uniform(1000, 50000), data_assinatura=fake.date_this_month(),
#                         data_vigencia_inicio=fake.date_this_month(after_today=True), data_vigencia_fim=fake.future_date(end_date='+3y'),
#                         vigencia_meses=random.randint(1, 36), criado_por=admin_user,
#                     )
#                     self.stdout.write(f'  - AudespAjusteContratual (Ata) Criado: {audesp_ajuste.codigo_contrato_audesp}')

#                 # --- Gerar AudespAtaRegistroPrecos (sua "Ata RP") ---
#                 ata_rp = None
#                 if edital and edital.status in ['PUBLICADO', 'ABERTO']:
#                     if random.random() > 0.5:
#                         itens_licitados_ids_ata = list(ItemLicitado.objects.filter(edital=edital).values_list('pk', flat=True))
#                         if not itens_licitados_ids_ata and edital:
#                             lote_dummy_rp = Lote.objects.create(edital=edital, numero_lote='200-D', descricao='Lote Dummy para Ata RP', valor_estimado_lote=50.00)
#                             item_dummy_rp = ItemLicitado.objects.create(lote=lote_dummy_rp, descricao_item='Item Dummy Ata RP', quantidade=5, unidade_medida='UN', valor_referencia=5.00, numero_item_audesp=1, material_ou_servico='M', tipo_beneficio=1, orcamento_sigiloso=False, valor_unitario_estimado_audesp=5.0000, valor_total_audesp=25.0000, criterio_julgamento=1, item_categoria=1)
#                             itens_licitados_ids_ata.append(item_dummy_rp.pk)

#                         ata_rp = AudespAtaRegistroPrecos.objects.create(
#                             processo_vinculado=processo, edital_origem=edital,
#                             municipio=audesp_config.municipio_codigo_audesp, entidade=audesp_config.entidade_codigo_audesp,
#                             codigo_edital_audesp=edital.numero_edital,
#                             codigo_ata_audesp=f'ATA-RP-{timezone.now().year}-{random.randint(100, 999):03d}-{i+1}', ano_compra=timezone.now().year,
#                             retificacao=random.choice([True, False]), itens_licitados_ids=itens_licitados_ids_ata,
#                             numero_ata_registro_preco=f'ARP-{timezone.now().year}-{random.randint(1000, 9999):04d}', ano_ata=timezone.now().year,
#                             data_assinatura=fake.date_this_month(), data_vigencia_inicio=fake.date_this_month(after_today=True),
#                             data_vigencia_fim=fake.future_date(end_date='+2y'),
#                             criado_por=admin_user,
#                         )
#                         self.stdout.write(f'  - Ata de Registro de Preços Criada: {ata_rp.codigo_ata_audesp}')
                
#                 # --- Gerar AudespEmpenhoContrato ---
#                 empenho = None
#                 if (audesp_ajuste or df) and random.random() > 0.6:
#                     empenho_codigo_contrato_audesp = audesp_ajuste.codigo_contrato_audesp if audesp_ajuste else fake.bothify(text='CONTRATO-###')
#                     empenho = AudespEmpenhoContrato.objects.create(
#                         ajuste_contratual_audesp=audesp_ajuste, documento_fiscal_origem=df, processo_vinculado=processo,
#                         municipio=audesp_config.municipio_codigo_audesp, entidade=audesp_config.entidade_codigo_audesp,
#                         codigo_contrato_audesp=empenho_codigo_contrato_audesp, retificacao=random.choice([True, False]),
#                         numero_empenho=f'EMP-{timezone.now().year}-{random.randint(10000, 99999):05d}', ano_empenho=timezone.now().year,
#                         data_emissao_empenho=fake.date_this_month(), criado_por=admin_user,
#                     )
#                     self.stdout.write(f'  - Empenho de Contrato Criado: {empenho.numero_empenho}')


#                 # --- Submissão AUDESP (App Integracao_AUDESP) ---
#                 if etp:
#                     SubmissaoAudesp.objects.create(
#                         content_object=etp, tipo_documento='ETP', status=random.choice(['GERADO', 'ENVIADO', 'VALIDADO']),
#                         enviado_por=admin_user, mensagem_status='JSON de ETP gerado/enviado para AUDESP (simulado).'
#                     )
#                 if tr:
#                     SubmissaoAudesp.objects.create(
#                         content_object=tr, tipo_documento='TR', status=random.choice(['GERADO', 'ENVIADO', 'VALIDADO']),
#                         enviado_por=admin_user, mensagem_status='JSON de TR gerado/enviado para AUDESP (simulado).'
#                     )
#                 if edital:
#                     SubmissaoAudesp.objects.create(
#                         content_object=edital, tipo_documento='EDL', status=random.choice(['GERADO', 'ENVIADO', 'VALIDADO', 'REJEITADO']),
#                         enviado_por=admin_user, mensagem_status='JSON de Edital gerado/enviado para AUDESP (simulado).'
#                     )
#                 if resultado:
#                     SubmissaoAudesp.objects.create(
#                         content_object=resultado, tipo_documento='RSL', status=random.choice(['GERADO', 'ENVIADO', 'VALIDADO']),
#                         enviado_por=admin_user, mensagem_status='JSON de Resultado de Licitação gerado/enviado para AUDESP (simulado).'
#                     )
#                 if df:
#                     SubmissaoAudesp.objects.create(
#                         content_object=df, tipo_documento='DF', status=random.choice(['GERADO', 'ENVIADO']),
#                         enviado_por=admin_user, mensagem_status='JSON de Documento Fiscal gerado para AUDESP (simulado).'
#                     )
#                 if audesp_ajuste_forced:
#                     SubmissaoAudesp.objects.create(
#                         content_object=audesp_ajuste_forced, tipo_documento='AJT',
#                         status=random.choice(['GERADO', 'ENVIADO', 'VALIDADO']), enviado_por=admin_user,
#                         mensagem_status='JSON de Ajuste/Ata AUDESP gerado/enviado (simulado) - FORÇADO.'
#                     )
#                 if ata_rp_forced:
#                     SubmissaoAudesp.objects.create(
#                         content_object=ata_rp_forced, tipo_documento='ARP',
#                         status=random.choice(['GERADO', 'ENVIADO', 'VALIDADO']), enviado_por=admin_user,
#                         mensagem_status='JSON de Ata de Registro de Preços gerado/enviado (simulado) - FORÇADO.'
#                     )
#                 if empenho_forced:
#                     SubmissaoAudesp.objects.create(
#                         content_object=empenho_forced, tipo_documento='EMP',
#                         status=random.choice(['GERADO', 'ENVIADO', 'VALIDADO']), enviado_por=admin_user,
#                         mensagem_status='JSON de Empenho de Contrato gerado/enviado (simulado) - FORÇADO.'
#                     )
                
#             self.stdout.write(self.style.SUCCESS(f'\nPopulação de {num_processos_completos_aleatorios} processos completos FINALIZADA com sucesso!')) 
#             self.stdout.write(self.style.WARNING('Lembre-se de verificar o Django Admin e navegar pelo sistema com os novos dados!'))
#             self.stdout.write(self.style.WARNING('Para gerar arquivos físicos para anexos (PDFs, etc.), será necessário implementar a lógica com ContentFile e um diretório MEDIA_ROOT configurado e acessível para escrita.'))


# SysGov_Project/core/management/commands/populate_data.py

import os
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings

# Importe todos os modelos necessários de todos os seus apps
from core.models import Processo, ArquivoAnexo
from contratacoes.models import ETP, TR, PCA, ItemPCA, PesquisaPreco, ParecerTecnico
from licitacoes.models import Edital, Lote, ItemLicitado, ResultadoLicitacao
from financeiro.models import DocumentoFiscal, Pagamento

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados fictícios para demonstração do ProGestor Público.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_processos',
            type=int,
            default=10,
            help='O número de processos completos a serem criados.',
        )

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        num_processos_completos = options['num_processos']
        
        self.stdout.write(self.style.WARNING('Iniciando a população de dados fictícios...'))
        
        # --- 1. Obter ou Criar Usuário Admin para vincular os Processos ---
        self.stdout.write(self.style.WARNING('Verificando superusuário...'))
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Usuário 'admin' não encontrado. Por favor, crie um superusuário primeiro ('python manage.py createsuperuser')."))
            return
        
        # --- Limpar dados existentes (Obrigatório para UNIQUE constraint) ---
        self.stdout.write(self.style.WARNING('Deletando dados antigos...'))
        try:
            with transaction.atomic():
                Processo.objects.all().delete()
                ETP.objects.all().delete()
                TR.objects.all().delete()
                Edital.objects.all().delete()
                ResultadoLicitacao.objects.all().delete()
                DocumentoFiscal.objects.all().delete()
                Pagamento.objects.all().delete()
                ArquivoAnexo.objects.all().delete()
                PCA.objects.all().delete()
                ItemPCA.objects.all().delete()
                
                # Deletar arquivos físicos da pasta de mídia
                media_root_path = settings.MEDIA_ROOT
                if os.path.exists(media_root_path):
                    import shutil
                    shutil.rmtree(media_root_path)
                    os.makedirs(media_root_path)
                    self.stdout.write(self.style.SUCCESS(f'Pasta de mídia "{media_root_path}" limpa.'))

            self.stdout.write(self.style.SUCCESS('Dados antigos deletados com sucesso.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao deletar dados antigos: {e}'))
            return

        # --- 2. Gerar Planos de Contratações Anuais (PCA) e Itens ---
        pcas = []
        for i in range(2):
            pca = PCA.objects.create(
                ano_vigencia=timezone.now().year + i,
                data_aprovacao=fake.date_this_year(),
                responsavel_aprovacao=admin_user,
                titulo=f'PCA do Ano {timezone.now().year + i}'
            )
            pcas.append(pca)
            self.stdout.write(f'  Criado PCA {pca.ano_vigencia}.')

            for j in range(5): # 5 itens por PCA
                ItemPCA.objects.create(
                    pca=pca,
                    identificador_item=f'ITEM-{pca.ano_vigencia}-{j+1:03d}',
                    descricao_item=fake.catch_phrase(),
                    valor_estimado_pca=random.uniform(5000.00, 500000.00),
                    unidade_requisitante=fake.company_suffix().upper(),
                )
        self.stdout.write(self.style.SUCCESS(f'Gerados {len(pcas)*5} Itens PCA.'))

        # --- 3. Gerar Processos Completos ---
        self.stdout.write(self.style.WARNING(f'Gerando {num_processos_completos} processos completos...'))

        for i in range(num_processos_completos):
            # Crie o Processo Principal (Core App)
            processo = Processo.objects.create(
                usuario=admin_user,
                titulo=fake.sentence(nb_words=6),
                descricao=fake.paragraph(nb_sentences=3),
                numero_protocolo=f'{timezone.now().year}/{random.randint(1000, 9999)}-PMB',
                status='EM_ANALISE'
            )
            self.stdout.write(f'\nProcesso Criado: {processo.numero_protocolo} - "{processo.titulo}"')

            # --- ETP (Contratacoes App) ---
            etp_status = random.choice(['APROVADO', 'REPROVADO', 'EM_ELABORACAO'])
            etp = ETP.objects.create(
                processo_vinculado=processo,
                titulo=f'ETP - {processo.titulo}',
                numero_processo=f'ETP-{processo.numero_protocolo}',
                setor_demandante=fake.company_suffix(),
                autor=admin_user,
                descricao_necessidade=fake.paragraph(nb_sentences=5),
                objetivo_contratacao=fake.sentence(),
                requisitos_contratacao=fake.paragraph(nb_sentences=4),
                levantamento_solucoes_mercado=fake.paragraph(nb_sentences=5),
                estimativa_quantidades=f'{random.randint(1, 100)} {fake.word()}',
                estimativa_valor=random.uniform(10000.00, 1000000.00),
                resultados_esperados=fake.paragraph(nb_sentences=3),
                viabilidade_justificativa_solucao=fake.paragraph(nb_sentences=4),
                alinhamento_planejamento=fake.paragraph(nb_sentences=2),
                status=etp_status,
                item_pca_vinculado=random.choice(ItemPCA.objects.all())
            )
            self.stdout.write(f'  - ETP Criado (Status: {etp.get_status_display()}).')
            for _ in range(3):
                PesquisaPreco.objects.create(
                    etp=etp,
                    fornecedor=fake.company(),
                    valor_cotado=random.uniform(etp.estimativa_valor * 0.8, etp.estimativa_valor * 1.2),
                    data_pesquisa=fake.date_this_year(),
                )
            if etp_status in ['EM_ANALISE', 'AGUARDANDO_REVISAO', 'REPROVADO']:
                etp.status = 'AGUARDANDO_REVISAO'
                etp.save()
            self.stdout.write(f'    - 3 Pesquisas de Preço adicionadas ao ETP.')
            
            # --- TR (Contratacoes App) ---
            if etp_status == 'APROVADO':
                tr = TR.objects.create(
                    processo_vinculado=processo,
                    etp_origem=etp,
                    titulo=f'TR - {processo.titulo}',
                    numero_processo=f'TR-{processo.numero_protocolo}',
                    data_criacao=fake.date_this_month(),
                    autor=admin_user,
                    objeto=fake.paragraph(nb_sentences=4),
                    justificativa=fake.paragraph(nb_sentences=3),
                    especificacoes_tecnicas=fake.paragraph(nb_sentences=5),
                    prazo_execucao_entrega='30 dias',
                    estimativa_preco_tr=etp.estimativa_valor * random.uniform(0.9, 1.1),
                    status='APROVADO'
                )
                self.stdout.write(f'  - TR Criado e APROVADO.')

                # --- Edital (Licitacoes App) ---
                edital = Edital.objects.create(
                    processo_vinculado=processo,
                    numero_edital=f'ED-{processo.numero_protocolo.split("/")[0]}-{random.randint(1, 50):02d}',
                    titulo=f'Edital - {processo.titulo}',
                    tipo_licitacao=random.choice(['PREGAO_ELETRONICO', 'CONCORRENCIA']),
                    data_publicacao=fake.date_this_month(),
                    data_abertura_propostas=fake.date_time_this_month(before_now=False, after_now=True),
                    valor_estimado=tr.estimativa_preco_tr,
                    status='PUBLICADO',
                    responsavel_publicacao=admin_user,
                    link_edital_completo=fake.url()
                )
                self.stdout.write(f'  - Edital Criado.')

                # --- Resultado da Licitação (Licitacoes App) ---
            if random.random() > 0.3:
                resultado = ResultadoLicitacao.objects.create(
                    edital=edital,
                    fornecedor_vencedor=fake.company(),
                    cnpj_vencedor=fake.cnpj(),
                    valor_homologado=random.uniform(edital.valor_estimado * 0.8, edital.valor_estimado * 0.95),
                    data_homologacao=fake.date_this_month(),
                    responsavel_registro=admin_user,
                    valor_estimado_inicial=edital.valor_estimado
                )
                edital.status = 'HOMOLOGADO'
                edital.save()
                self.stdout.write(f'  - Resultado da Licitação Registrado (Vencedor: {resultado.fornecedor_vencedor}).')

                # <<< MOVIDO PARA AQUI: A CRIAÇÃO DO ANEXO AGORA ESTÁ DENTRO DESTE IF >>>
                anexo_pdf_content = "Conteúdo fictício do PDF para demonstrar anexo.".encode('utf-8')
                anexo_filename = f'Ata-Edital-{edital.numero_edital.replace("/", "-")}.pdf'
                
                media_root_path = settings.MEDIA_ROOT
                os.makedirs(os.path.join(media_root_path, 'anexos_gerais', f'{timezone.now().year}', f'{timezone.now().month:02d}', f'{timezone.now().day:02d}'), exist_ok=True)
                
                from django.core.files.storage import default_storage
                from django.core.files.base import ContentFile
                
                file_path = os.path.join('anexos_gerais', f'{timezone.now().year}', f'{timezone.now().month:02d}', f'{timezone.now().day:02d}', anexo_filename)
                default_storage.save(file_path, ContentFile(anexo_pdf_content))

                anexo = ArquivoAnexo.objects.create(
                    titulo=f'Anexo PDF do Edital {edital.numero_edital}',
                    arquivo=file_path,
                    uploaded_by=admin_user,
                    content_object=processo
                )
                self.stdout.write(f'  - Anexo Genérico criado para o Processo ({anexo_filename}).')
                # <<< FIM DO TRECHO MOVIDO >>>

            else:
                edital.status = random.choice(['ENCERRADO', 'FRACASSADO'])
                edital.save()
                self.stdout.write(f'  - Edital Encerrado/Fracassado (Status: {edital.get_status_display()}).')
                
                # --- Documento Fiscal e Pagamento (Financeiro App) ---
                if edital.status == 'HOMOLOGADO' and edital.resultados.exists():
                    resultado_vencedor = edital.resultados.first()
                    df = DocumentoFiscal.objects.create(
                        processo_vinculado=processo,
                        codigo_ajuste=f'AJUSTE-{processo.numero_protocolo.split("/")[0]}-{random.randint(1, 10):02d}',
                        medicao_numero=1,
                        nota_empenho_numero=f'EMP-{processo.numero_protocolo.split("/")[0]}-{random.randint(1, 50):02d}',
                        nota_empenho_data_emissao=fake.date_this_month(),
                        documento_fiscal_numero=f'NF-{random.randint(10000, 99999)}',
                        documento_fiscal_uf='SP',
                        documento_fiscal_valor=random.uniform(resultado_vencedor.valor_homologado, resultado_vencedor.valor_homologado * 1.05),
                        documento_fiscal_data_emissao=fake.date_this_month(),
                    )
                    self.stdout.write(f'  - Documento Fiscal Criado (NF: {df.documento_fiscal_numero}).')

                    if random.random() > 0.2:
                        Pagamento.objects.create(
                            processo_vinculado=processo,
                            codigo_ajuste=df.codigo_ajuste,
                            medicao_numero=df.medicao_numero,
                            nota_empenho_numero=df.nota_empenho_numero,
                            nota_empenho_data_emissao=df.nota_empenho_data_emissao,
                            documento_fiscal_numero=df.documento_fiscal_numero,
                            documento_fiscal_data_emissao=df.documento_fiscal_data_emissao,
                            documento_fiscal_uf=df.documento_fiscal_uf,
                            nota_fiscal_valor_pago=df.documento_fiscal_valor,
                            nota_fiscal_pagto_dt=fake.date_this_month(after_today=True),
                            recolhido_encargos_previdenciario=random.choice(['S', 'N']),
                        )
                        self.stdout.write(f'  - Pagamento Registrado (NF: {df.documento_fiscal_numero}).')
                
            # --- Anexo Genérico (Core App) ---
            anexo_pdf_content = "Conteúdo fictício do PDF para demonstrar anexo.".encode('utf-8')
            anexo_filename = f'Edital_Homologado_{edital.numero_edital.replace("/", "-")}.pdf'
            
            # Cria a pasta 'media' se não existir
            media_root_path = settings.MEDIA_ROOT
            os.makedirs(os.path.join(media_root_path, 'anexos_gerais', f'{timezone.now().year}', f'{timezone.now().month:02d}', f'{timezone.now().day:02d}'), exist_ok=True)
            
            # Cria o arquivo físico dummy
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            file_path = os.path.join('anexos_gerais', f'{timezone.now().year}', f'{timezone.now().month:02d}', f'{timezone.now().day:02d}', anexo_filename)
            default_storage.save(file_path, ContentFile(anexo_pdf_content))
            
            anexo = ArquivoAnexo.objects.create(
                titulo=f'Anexo PDF do Edital {edital.numero_edital}',
                arquivo=file_path,
                uploaded_by=admin_user,
                content_object=processo
            )
            self.stdout.write(f'  - Anexo Genérico criado para o Processo ({anexo_filename}).')

        self.stdout.write(self.style.SUCCESS(f'\nPopulação de {num_processos_completos} processos completos FINALIZADA com sucesso!'))