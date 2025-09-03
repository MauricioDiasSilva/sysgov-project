# [nome_do_app]/management/commands/populate_data.py

import random
from faker import Faker
from decimal import Decimal
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction

# Importações dos modelos
from django.contrib.auth.models import User, Group
from core.models import Processo, Fornecedor
from contratacoes.models import PCA, ItemPCA, ETP, TR, Contrato
from licitacoes.models import Edital, ItemLicitado, Pregao, ParticipanteLicitacao, Lance
from financeiro.models import NotaEmpenho

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de teste completos para o SysGov'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando a população do banco de dados...")
        
        with transaction.atomic():
            self.limpar_dados()
            self.criar_grupos_e_usuarios()
            # Cria 5 cenários de licitação completos
            for i in range(5):
                self.stdout.write(f"\n--- Criando cenário de licitação completo {i+1}/5 ---")
                self.criar_cenario_completo()
        
        self.stdout.write(self.style.SUCCESS("\nPopulação de dados concluída com sucesso!"))

    def limpar_dados(self):
        self.stdout.write("  Deletando dados antigos...")
        Lance.objects.all().delete()
        ParticipanteLicitacao.objects.all().delete()
        NotaEmpenho.objects.all().delete()
        Contrato.objects.all().delete()
        Pregao.objects.all().delete()
        ItemLicitado.objects.all().delete()
        Edital.objects.all().delete()
        TR.objects.all().delete()
        ETP.objects.all().delete()
        ItemPCA.objects.all().delete()
        PCA.objects.all().delete()
        Processo.objects.all().delete()
        Fornecedor.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Group.objects.all().delete()
        self.stdout.write("  Limpeza concluída.")

    def criar_grupos_e_usuarios(self):
        self.stdout.write("  Criando grupos e usuários de teste...")
        fake = Faker('pt_BR')
        grupos_nomes = ['Secretarias', 'Analise de Requerimentos', 'Setor de Orcamento', 'Comissao de Licitacao']
        for nome in grupos_nomes:
            Group.objects.get_or_create(name=nome)

        for nome_grupo in grupos_nomes:
            grupo = Group.objects.get(name=nome_grupo)
            username = nome_grupo.lower().replace(' ', '_')
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='123', email=fake.email())
                user.groups.add(grupo)

    def criar_cenario_completo(self):
        fake = Faker('pt_BR')
        
        secretaria_user = User.objects.get(username='secretarias')
        analise_user = User.objects.get(username='analise_de_requerimentos')
        orcamento_user = User.objects.get(username='setor_de_orcamento')
        pregoeiro_user = User.objects.get(username='comissao_de_licitacao')

        fornecedores = [Fornecedor.objects.create(razao_social=fake.company(), cnpj=fake.cnpj()) for _ in range(3)]

        pca, _ = PCA.objects.get_or_create(
            ano_vigencia=timezone.now().year,
            defaults={'data_aprovacao': timezone.now().date(), 'responsavel_aprovacao': pregoeiro_user}
        )
        item_pca = ItemPCA.objects.create(
            pca=pca,
            identificador_item=f"ITEM-{pca.ano_vigencia}-{random.randint(100, 999)}",
            descricao_item=fake.sentence(nb_words=8),
            valor_estimado_pca=Decimal(random.uniform(10000, 50000)),
            unidade_requisitante="Secretaria de Testes"
        )

        processo = Processo.objects.create(
            usuario=secretaria_user,
            titulo=f"Processo de Aquisição: {fake.bs()}",
            numero_protocolo=f"{random.randint(1000, 9999)}/{timezone.now().year}"
        )

        etp = ETP.objects.create(
            processo_vinculado=processo,
            titulo=f"ETP para {processo.titulo}",
            numero_processo=processo.numero_protocolo,
            setor_demandante="Secretaria de Testes",
            autor=secretaria_user,
            descricao_necessidade=fake.paragraph(),
            objetivo_contratacao=fake.paragraph(),
            requisitos_contratacao=fake.paragraph(),
            estimativa_quantidades=fake.paragraph(),
            estimativa_valor=item_pca.valor_estimado_pca * Decimal(random.uniform(0.9, 1.1)),
            status='APROVADO'
        )

        tr = TR.objects.create(
            etp_origem=etp, processo_vinculado=processo, titulo=f"TR para {etp.titulo}",
            numero_processo=processo.numero_protocolo, autor=analise_user, objeto=etp.objetivo_contratacao,
            status='APROVADO'
        )
        
        edital = Edital.objects.create(
            processo_vinculado=processo, numero_edital=f"{random.randint(1, 100)}/{timezone.now().year}",
            titulo=tr.objeto, data_publicacao=timezone.now().date(),
            data_abertura_propostas=timezone.now() + timezone.timedelta(days=15),
            status='PUBLICADO'
        )
        item_licitado = ItemLicitado.objects.create(
            edital=edital, descricao_item=tr.objeto, quantidade=10, unidade_medida="Unidade"
        )
        
        pregao = Pregao.objects.create(
            edital=edital, pregoeiro=pregoeiro_user,
            data_abertura_sessao=edital.data_abertura_propostas, status='ABERTO_PARA_LANCES'
        )

        participantes = [ParticipanteLicitacao.objects.create(pregao=pregao, fornecedor=forn) for forn in fornecedores]

        lances = [Lance.objects.create(
            participante=p, item=item_licitado,
            valor_lance=etp.estimativa_valor * Decimal(random.uniform(0.8, 1.2))
        ) for p in participantes]

        lance_vencedor = min(lances, key=lambda x: x.valor_lance)
        lance_vencedor.aceito = True
        lance_vencedor.save()
        fornecedor_vencedor = lance_vencedor.participante.fornecedor

        contrato = Contrato.objects.create(
            processo_vinculado=processo, licitacao_origem=edital, contratado=fornecedor_vencedor,
            numero_contrato=f"CT-{random.randint(100, 999)}", ano_contrato=timezone.now().year,
            objeto=edital.titulo, valor_total=lance_vencedor.valor_lance,
            data_assinatura=timezone.now().date(), data_inicio_vigencia=timezone.now().date(),
            data_fim_vigencia=timezone.now().date() + timezone.timedelta(days=365)
        )

        NotaEmpenho.objects.create(
            contrato=contrato, fornecedor=fornecedor_vencedor, numero_empenho=f"NE-{random.randint(1000, 9999)}",
            ano_empenho=timezone.now().year, data_emissao=timezone.now().date(),
            valor=contrato.valor_total, descricao=f"Empenho referente ao contrato {contrato.numero_contrato}"
        )   