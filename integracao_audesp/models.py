# SysGov_Project/integracao_audesp/models.py

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import Processo # Importação necessária para ForeignKeys
from licitacoes.models import Edital, ResultadoLicitacao # Importação necessária para ForeignKeys
from financeiro.models import DocumentoFiscal # Importação necessária para ForeignKeys (DocumentoFiscal)


# --- CHOICES para os modelos AUDESP (baseado no schema PNCP/AUDESP) ---
AUDESP_TIPO_CONTRATO_CHOICES = [
    (1, 'Contrato Original'), (2, 'Termo Aditivo'), (3, 'Apostilamento'),
    (4, 'Rescisão Contratual'), (5, 'Reajuste'), (7, 'Supressão'),
    (8, 'Acrescimento'), (12, 'Outros')
]

AUDESP_CATEGORIA_PROCESSO_CHOICES = [
    (1, 'Licitação'), (2, 'Dispensa de Licitação'), (3, 'Inexigibilidade de Licitação'),
    (4, 'Concurso'), (5, 'Leilão'), (6, 'Concessão de Serviço Público'),
    (7, 'Permissão de Serviço Público'), (8, 'Parceria Público-Privada (PPP)'),
    (9, 'Convênio'), (10, 'Termo de Fomento'), (11, 'Termo de Colaboração')
]

AUDESP_TIPO_PESSOA_CHOICES = [
    ('PJ', 'Pessoa Jurídica'), ('PF', 'Pessoa Física'), ('PE', 'Estrangeiro')
]

AUDESP_TIPO_OBJETO_CONTRATO_CHOICES = [
    (1, 'Aquisição de Bens'), (2, 'Prestação de Serviços'), (3, 'Obras e Serviços de Engenharia'),
    (4, 'Locação de Imóveis'), (5, 'Alienação de Bens'), (6, 'Concessão de Uso'),
    (7, 'Permissão de Uso'), (8, 'Doação'), (9, 'Acordos de Cooperação'),
    (10, 'Outros Contratos Administrativos'), (11, 'Gestão e Manutenção'), (12, 'Tecnologia da Informação'),
    (13, 'Comunicação e Publicidade'), (14, 'Eventos e Festividades'), (15, 'Transporte e Logística'),
    (16, 'Saúde e Assistência Social'), (17, 'Educação e Cultura'), (18, 'Meio Ambiente'),
    (19, 'Urbanismo e Infraestrutura'), (20, 'Segurança e Vigilância'), (21, 'Serviços de Consultoria'),
    (22, 'Alimentos e Bebidas'), (23, 'Vestuário e Equipamentos'), (24, 'Combustíveis e Lubrificantes'),
    (25, 'Materiais de Consumo'), (26, 'Equipamentos e Máquinas'), (27, 'Softwares e Sistemas'),
    (28, 'Veículos'), (29, 'Mobiliário')
]

# --- NOVO: CHOICES Específicos para AudespEditalDetalhado (do esquema 'licitacoes v-4') ---
AUDESP_RECURSO_BID_CHOICES = [
    (1, 'Sim'), (2, 'Não'), (3, 'Não se aplica')
]

AUDESP_OBJECION_BID_CHOICES = [ # Para aberturaPreQualificacaoBID, editalPreQualificacaoBID, julgamentoPreQualificacaoBID, etc.
    (1, 'Houve Objeção'), (2, 'Não Houve Objeção'), (3, 'Não se aplica')
]

AUDESP_TIPO_NATUREZA_CHOICES = [
    (1, 'Compras'), (2, 'Serviços'), (3, 'Obras'), (4, 'Alienações'),
    (5, 'Concessões'), (6, 'Permissões'), (7, 'Doações'), (8, 'Outros')
]

AUDESP_INTERPOSICAO_RECURSO_CHOICES = [ # Reuso para viabilidade, audiencia, visitaTecnica
    (1, 'Sim'), (2, 'Não'), (3, 'Não se aplica')
]

AUDESP_EXIGENCIA_GARANTIA_CHOICES = [
    (1, 'Sim'), (2, 'Não'), (3, 'Não se aplica')
]

AUDESP_EXIGENCIA_AMOSTRA_CHOICES = [
    (1, 'Sim'), (2, 'Não'), (3, 'Não se aplica')
]

AUDESP_EXIGENCIA_INDICES_ECONOMICOS_CHOICES = [
    (1, 'Sim'), (2, 'Não'), (3, 'Não se aplica')
]

AUDESP_TIPO_INDICE_CHOICES = [
    (1, 'Liquidez Corrente'), (2, 'Liquidez Geral'), (3, 'Endividamento Total'),
    (4, 'Rentabilidade sobre Vendas'), (5, 'Grau de Alavancagem'),
    (6, 'Margem Operacional'), (7, 'Outros'), (8, 'Não se aplica')
]

AUDESP_TIPO_ORCAMENTO_CHOICES = [
    (0, 'Não Informado'), (1, 'Valor Médio'), (2, 'Valor Mediano'), (3, 'Menor Preço')
]

AUDESP_SITUACAO_COMPRA_ITEM_CHOICES = [
    (1, 'Em Andamento'), (2, 'Suspensa'), (3, 'Cancelada'), (4, 'Adjudicada'), (5, 'Homologada')
]

AUDESP_TIPO_VALOR_PROPOSTA_CHOICES = [
    ('M', 'Monetário'), ('P', 'Percentual')
]

AUDESP_TIPO_PROPOSTA_CHOICES = [
    (1, 'Inicial'), (2, 'Reajustada'), (3, 'Final')
]

AUDESP_DECLARACAO_ME_EPP_CHOICES = [
    (1, 'Sim'), (2, 'Não'), (3, 'Não se aplica') # 3 aqui pode ser 'Não Declarou'
]

AUDESP_RESULTADO_HABILITACAO_CHOICES = [
    (1, 'Habilitado'), (2, 'Inabilitado'), (3, 'Recurso Aguardando Análise'),
    (4, 'Recurso Deferido'), (5, 'Recurso Indeferido'), (6, 'Convocado'), (7, 'Não se aplica')
]

class AudespEditalDetalhado(models.Model):
    """
    Representa o JSON schema para o envio de Editais de licitação/compra
    em sua versão MAIS DETALHADA (licitacoes v-4), incluindo campos de BID.
    """
    # Relacionamento com o Edital "principal" do SysGov
    edital_principal = models.OneToOneField(
        'licitacoes.Edital', # Referência para o Edital do app licitacoes
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='audesp_edital_detalhado',
        verbose_name="Edital Principal (SysGov)",
        help_text="O Edital de licitação no sistema principal ao qual este detalhamento se refere."
    )
    # Relacionamento com o processo principal
    processo_vinculado = models.ForeignKey(
        'core.Processo', # Referência para o Processo do app core
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='audesp_edital_detalhados',
        verbose_name="Processo Principal (SysGov)"
    )


    # --- Campos do 'descritor' ---
    municipio = models.IntegerField(verbose_name="Município (Cód. AUDESP)")
    entidade = models.IntegerField(verbose_name="Entidade (Cód. AUDESP)")
    codigo_edital_audesp = models.CharField(max_length=25, verbose_name="Código Edital (AUDESP)")
    retificacao = models.BooleanField(default=False, verbose_name="É Retificação (AUDESP)")


    # --- Campos Principais do Edital Detalhado ---
    recurso_bid = models.IntegerField(
        choices=AUDESP_RECURSO_BID_CHOICES,
        verbose_name="Recursos BID Envolvidos"
    )
    abertura_pre_qualificacao_bid = models.IntegerField(
        choices=AUDESP_OBJECION_BID_CHOICES,
        verbose_name="Objeção BID Abertura Pré-qualificação",
        null=True, blank=True
    )
    edital_pre_qualificacao_bid = models.IntegerField(
        choices=AUDESP_OBJECION_BID_CHOICES,
        verbose_name="Objeção BID Edital Pré-qualificação",
        null=True, blank=True
    )
    julgamento_pre_qualificacao_bid = models.IntegerField(
        choices=AUDESP_OBJECION_BID_CHOICES,
        verbose_name="Objeção BID Julgamento Pré-qualificação",
        null=True, blank=True
    )
    edital_2_fase_bid = models.IntegerField(
        choices=AUDESP_OBJECION_BID_CHOICES,
        verbose_name="Objeção BID Edital 2ª Fase",
        null=True, blank=True
    )
    julgamento_propostas_bid = models.IntegerField(
        choices=AUDESP_OBJECION_BID_CHOICES,
        verbose_name="Objeção BID Julgamento Propostas",
        null=True, blank=True
    )
    julgamento_negociacao_bid = models.IntegerField(
        choices=AUDESP_OBJECION_BID_CHOICES,
        verbose_name="Objeção BID Julgamento Negociação Final",
        null=True, blank=True
    )
    tipo_natureza = models.IntegerField(
        choices=AUDESP_TIPO_NATUREZA_CHOICES,
        verbose_name="Tipo de Natureza"
    )
    viabilidade_contratacao = models.IntegerField(
        choices=AUDESP_INTERPOSICAO_RECURSO_CHOICES,
        verbose_name="Viabilidade da Contratação",
        null=True, blank=True
    )
    interposicao_recurso = models.IntegerField(
        choices=AUDESP_INTERPOSICAO_RECURSO_CHOICES,
        verbose_name="Houve Interposição de Recurso"
    )
    audiencia_publica = models.IntegerField(
        choices=AUDESP_INTERPOSICAO_RECURSO_CHOICES,
        verbose_name="Houve Audiência Pública",
        null=True, blank=True
    )
    exigencia_garantia_licitantes = models.IntegerField(
        choices=AUDESP_EXIGENCIA_GARANTIA_CHOICES,
        verbose_name="Exigência de Garantia para Licitantes"
    )
    percentual_valor_garantia = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Percentual do Valor da Garantia"
    )
    exigencia_amostra = models.IntegerField(
        choices=AUDESP_EXIGENCIA_AMOSTRA_CHOICES,
        verbose_name="Exigência de Amostra"
    )
    quitacao_tributos_federais = models.BooleanField(
        verbose_name="Exige Quitação Tributos Federais"
    )
    quitacao_tributos_estaduais = models.BooleanField(
        verbose_name="Exige Quitação Tributos Estaduais"
    )
    quitacao_tributos_municipais = models.BooleanField(
        verbose_name="Exige Quitação Tributos Municipais"
    )
    exigencia_visita_tecnica = models.IntegerField(
        choices=AUDESP_INTERPOSICAO_RECURSO_CHOICES,
        verbose_name="Exigência de Visita Técnica",
        null=True, blank=True
    )
    exigencia_curriculo = models.BooleanField(
        verbose_name="Exigência de Currículo (Visita Técnica)"
    )
    exigencia_visto_crea = models.BooleanField(
        verbose_name="Exigência de Visto CREA/SP (Outros Estados)"
    )
    declaracao_recursos_orcamentarios = models.BooleanField(
        verbose_name="Declaração de Recursos Orçamentários"
    )
    fonte_recursos_contratacao_detalhada = models.JSONField(
        default=list, blank=True, null=True,
        verbose_name="Fontes de Recursos da Contratação",
        help_text="Lista de fontes de recursos que constam na declaração da existência de recursos orçamentários para a contratação (array de números)."
    )

    contratacao_conduzida = models.BooleanField(
        verbose_name="Contratação Conduzida por Agente/Comissão"
    )
    cpfs_condutores = models.JSONField(
        default=list, blank=True, null=True,
        verbose_name="CPFs dos Condutores",
        help_text="Lista de CPFs dos condutores da licitação (array de objetos com 'cpfCondutor')."
    )
    exigencia_indices_economicos = models.IntegerField(
        choices=AUDESP_EXIGENCIA_INDICES_ECONOMICOS_CHOICES,
        verbose_name="Exigência de Índices Econômicos Mínimos"
    )
    indices_economicos = models.JSONField(
        default=list, blank=True, null=True,
        verbose_name="Índices Econômicos",
        help_text="Lista de índices econômicos (array de objetos com tipoIndice, nomeIndice, valorIndice)."
    )

    # Nota: O schema tem um array 'itens' com uma estrutura muito detalhada de itens e licitantes
    # Isso sugere que pode ser necessário um modelo separado para ItemLicitadoDetalhado
    # ou uma abordagem mais complexa de JSONField se a estrutura de ItemLicitado existente não for suficiente.
    # Por simplicidade e para não duplicar muito ItemLicitado, vamos usar uma FK/ManyToMany para o existente e um JSONField para os extras se não couberem.
    # O mapeamento para 'itensCompra' no JSON será feito na view de geração, buscando dados de ItemLicitado existente
    # e, se necessário, de outros modelos relacionados a licitantes/propostas ou criando dados em JSONField.

    class Meta:
        verbose_name = "AUDESP Edital Detalhado"
        verbose_name_plural = "AUDESP Editais Detalhados"
        ordering = ['-edital_principal__data_publicacao']
        # unique_together = ('municipio', 'entidade', 'codigo_edital_audesp') # Pode ser mais granular

    def __str__(self):
        return f"AUDESP Edital Detalhado: {self.codigo_edital_audesp} (Edital: {self.edital_principal.numero_edital if self.edital_principal else 'N/A'})"
    

    
class AudespConfiguracao(models.Model):
    """
    Modelo para armazenar configurações globais da integração com o AUDESP,
    como códigos do município e da entidade.
    """
    municipio_codigo_audesp = models.IntegerField(
        verbose_name="Código do Município (AUDESP)",
        help_text="Código do município conforme tabela do AUDESP/TCE-SP (ex: 7107 para Carapicuíba)."
    )
    entidade_codigo_audesp = models.IntegerField(
        verbose_name="Código da Entidade (AUDESP)",
        help_text="Código da entidade ou órgão da prefeitura conforme tabela do AUDESP/TCE-SP (ex: 10048)."
    )
    class Meta:
        verbose_name = "Configuração AUDESP"
        verbose_name_plural = "Configurações AUDESP"
    def __str__(self):
        return f"Config. AUDESP - Mun: {self.municipio_codigo_audesp}, Ent: {self.entidade_codigo_audesp}"

class SubmissaoAudesp(models.Model):
    """
    Registra cada tentativa de geração ou submissão de um documento para o AUDESP.
    Usa GenericForeignKey para vincular a qualquer modelo (ETP, TR, Edital, DF, Pagamento).
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    data_submissao = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora da Submissão")
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Enviado por"
    )
    TIPO_DOCUMENTO_CHOICES = [
        ('ETP', 'Estudo Técnico Preliminar'),
        ('TR', 'Termo de Referência'),
        ('EDL', 'Edital de Licitação'),
        ('DF', 'Documento Fiscal'),
        ('PG', 'Pagamento'),
        ('CTR', 'Contrato'),
        ('RSL', 'Resultado da Licitação'),
        ('AJT', 'Ajuste Contratual/Ata AUDESP'),
        ('ARP', 'Ata de Registro de Preços (AUDESP)'),
        ('EMP', 'Empenho de Contrato (AUDESP)'),
    ]
    tipo_documento = models.CharField(
        max_length=5,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de Documento AUDESP"
    )
    STATUS_SUBMISSAO_CHOICES = [
        ('GERADO', 'Gerado (JSON/XML)'),
        ('ERRO_GERACAO', 'Erro na Geração'),
        ('ENVIADO', 'Enviado ao AUDESP'),
        ('ERRO_ENVIO', 'Erro no Envio'),
        ('VALIDADO', 'Validado pelo AUDESP'),
        ('REJEITADO', 'Rejeitado pelo AUDESP'),
    ]
    status = models.CharField(
        max_length=15,
        choices=STATUS_SUBMISSAO_CHOICES,
        default='GERADO',
        verbose_name="Status da Submissão"
    )
    mensagem_status = models.TextField(
        blank=True, null=True,
        verbose_name="Mensagem de Status/Erro",
        help_text="Detalhes sobre o status da submissão ou erros ocorridos."
    )
    arquivo_gerado = models.FileField(
        upload_to='audesp_submissoes/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name="Arquivo Gerado (JSON/XML)"
    )

    class Meta:
        verbose_name = "Submissão AUDESP"
        verbose_name_plural = "Submissões AUDESP"
        ordering = ['-data_submissao']

    def __str__(self):
        return f"Submissão AUDESP de {self.get_tipo_documento_display()} ({self.content_object}) - Status: {self.get_status_display()}"


# ... (código anterior, incluindo CHOICES e AudespConfiguracao, SubmissaoAudesp)

class AudespAjusteContratual(models.Model):
    """
    Representa o schema JSON para envio de AJUSTES (formalizações contratuais, aditivos, etc.) para o AUDESP.
    """
    processo_vinculado = models.ForeignKey(
        Processo, on_delete=models.CASCADE, null=True, blank=True,
        related_name='audesp_ajustes_contratuais', verbose_name="Processo Principal (SysGov)"
    )
    resultado_licitacao_origem = models.OneToOneField(
        ResultadoLicitacao, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audesp_ajuste_contratual', verbose_name="Resultado da Licitação de Origem"
    )
    edital_origem = models.ForeignKey(
        Edital, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audesp_ajustes_contratuais_edital', verbose_name="Edital de Origem"
    )

    # Campos do 'descritor'
    adesao_participacao = models.BooleanField(default=False, verbose_name="Adesão ou Participação (AUDESP)")
    gerenciadora_jurisdicionada = models.BooleanField(default=False, verbose_name="Gerenciadora Jurisdicionada TCE-SP (AUDESP)", null=True, blank=True)
    cnpj_gerenciadora = models.CharField(max_length=14, blank=True, null=True, verbose_name="CNPJ Gerenciadora (AUDESP)")
    municipio_gerenciador = models.IntegerField(blank=True, null=True, verbose_name="Município Gerenciador (Cód. AUDESP)")
    entidade_gerenciadora = models.IntegerField(blank=True, null=True, verbose_name="Entidade Gerenciadora (Cód. AUDESP)")
    codigo_edital_audesp = models.CharField(max_length=25, blank=True, null=True, verbose_name="Código Edital (AUDESP)")
    codigo_ata_rp_audesp = models.CharField(max_length=30, blank=True, null=True, verbose_name="Código Ata RP (AUDESP)")
    codigo_contrato_audesp = models.CharField(max_length=25, unique=True, verbose_name="Código Ajuste/Contrato (AUDESP)")
    retificacao = models.BooleanField(default=False, verbose_name="É Retificação (AUDESP)")

    # Campos Principais do Schema
    fonte_recursos_contratacao = models.JSONField(default=list, blank=True, null=True, verbose_name="Fontes de Recursos")
    itens_contratados_ids = models.JSONField(default=list, blank=True, null=True, verbose_name="IDs dos Itens Contratados")
    tipo_contrato_id = models.IntegerField(choices=AUDESP_TIPO_CONTRATO_CHOICES, verbose_name="Tipo de Contrato (PNCP)")
    numero_contrato_empenho = models.CharField(max_length=50, verbose_name="Número Contrato/Empenho")
    ano_contrato = models.IntegerField(verbose_name="Ano do Contrato")
    processo_sistema_origem = models.CharField(max_length=50, verbose_name="Número Processo (Sistema Origem)")
    categoria_processo_id = models.IntegerField(choices=AUDESP_CATEGORIA_PROCESSO_CHOICES, verbose_name="Categoria do Processo (PNCP)")
    receita = models.BooleanField(verbose_name="Gera Receita para a Entidade?")
    despesas_classificacao = models.JSONField(default=list, blank=True, null=True, verbose_name="Classificações de Despesa")
    codigo_unidade = models.CharField(max_length=30, blank=True, null=True, verbose_name="Código da Unidade (PNCP)")
    ni_fornecedor = models.CharField(max_length=50, verbose_name="NI do Fornecedor")
    tipo_pessoa_fornecedor = models.CharField(max_length=2, choices=AUDESP_TIPO_PESSOA_CHOICES, verbose_name="Tipo de Pessoa Fornecedor")
    nome_razao_social_fornecedor = models.CharField(max_length=100, verbose_name="Nome/Razão Social Fornecedor")
    ni_fornecedor_subcontratado = models.CharField(max_length=50, blank=True, null=True, verbose_name="NI Fornecedor Subcontratado")
    tipo_pessoa_fornecedor_subcontratado = models.CharField(max_length=2, choices=AUDESP_TIPO_PESSOA_CHOICES, blank=True, null=True, verbose_name="Tipo Pessoa Fornecedor Subcontratado")
    nome_razao_social_fornecedor_subcontratado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome/Razão Social Fornecedor Subcontratado")
    objeto_contrato = models.TextField(max_length=5120, verbose_name="Objeto do Contrato")
    informacao_complementar = models.TextField(max_length=5120, blank=True, null=True, verbose_name="Informações Complementares")
    valor_inicial = models.DecimalField(max_digits=17, decimal_places=4, verbose_name="Valor Inicial do Ajuste (R$)")
    numero_parcelas = models.IntegerField(null=True, blank=True, verbose_name="Número de Parcelas")
    valor_parcela = models.DecimalField(max_digits=17, decimal_places=4, null=True, blank=True, verbose_name="Valor da Parcela (R$)")
    valor_global = models.DecimalField(max_digits=17, decimal_places=4, verbose_name="Valor Global do Ajuste (R$)")
    valor_acumulado = models.DecimalField(max_digits=17, decimal_places=4, verbose_name="Valor Acumulado do Ajuste (R$)")
    data_assinatura = models.DateField(verbose_name="Data de Assinatura")
    data_vigencia_inicio = models.DateField(verbose_name="Data de Início da Vigência")
    data_vigencia_fim = models.DateField(verbose_name="Data de Fim da Vigência")
    vigencia_meses = models.IntegerField(blank=True, null=True, verbose_name="Vigência em Meses")
    tipo_objeto_contrato = models.IntegerField(
        choices=AUDESP_TIPO_OBJETO_CONTRATO_CHOICES,
        verbose_name="Tipo de Objeto do Ajuste (PNCP)",
        null=True, blank=True # <<< ESSA LINHA PRECISA ESTAR AQUI (OU GARANTIR PREENCHIMENTO NO POPULADOR)
    )

    # Outros campos internos de gestão
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_ultima_atualizacao = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Criado Por")

    class Meta:
        verbose_name = "AUDESP Ajuste Contratual"
        verbose_name_plural = "AUDESP Ajustes Contratuais"
        ordering = ['-data_assinatura']

    def __str__(self):
        return f"Ajuste AUDESP {self.codigo_contrato_audesp} - {self.nome_razao_social_fornecedor}"

# ... (restante do seu models.py, incluindo AudespAtaRegistroPrecos e AudespEmpenhoContrato)


class AudespAtaRegistroPrecos(models.Model): # <<< Este é o modelo da Ata de Registro de Preços
    """
    Representa o schema JSON para envio de ATA de Registro de Preços para o AUDESP.
    """
    # Relacionamentos
    processo_vinculado = models.ForeignKey(
        Processo, on_delete=models.CASCADE, null=True, blank=True,
        related_name='atas_rp_audesp_processo', verbose_name="Processo Principal (SysGov)"
    )
    edital_origem = models.ForeignKey(
        Edital, on_delete=models.CASCADE,
        related_name='atas_rp_audesp_edital', verbose_name="Edital de Origem"
    )

    # Campos do 'descritor' do schema de Ata
    municipio = models.IntegerField(verbose_name="Município (Cód. AUDESP)")
    entidade = models.IntegerField(verbose_name="Entidade (Cód. AUDESP)")
    codigo_edital_audesp = models.CharField(max_length=30, verbose_name="Código do Edital (AUDESP)")
    codigo_ata_audesp = models.CharField(max_length=30, unique=True, verbose_name="Código da Ata (AUDESP)")
    ano_compra = models.IntegerField(verbose_name="Ano da Compra/Contratação")
    retificacao = models.BooleanField(default=False, verbose_name="É Retificação (AUDESP)")

    # Campos Principais do Esquema de Ata
    itens_licitados_ids = models.JSONField(default=list, blank=True, null=True, verbose_name="IDs dos Itens Licitados")
    numero_ata_registro_preco = models.CharField(max_length=30, verbose_name="Número da Ata de Registro de Preço")
    ano_ata = models.IntegerField(verbose_name="Ano da Ata")
    data_assinatura = models.DateField(verbose_name="Data de Assinatura")
    data_vigencia_inicio = models.DateField(verbose_name="Data de Início da Vigência")
    data_vigencia_fim = models.DateField(verbose_name="Data de Fim da Vigência")

    # Outros campos internos de gestão
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_ultima_atualizacao = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Criado Por")

    class Meta:
        verbose_name = "AUDESP Ata de Registro de Preços"
        verbose_name_plural = "AUDESP Atas de Registro de Preços"
        ordering = ['-data_assinatura']
        unique_together = ('municipio', 'entidade', 'codigo_ata_audesp', 'ano_ata')

    def __str__(self):
        return f"Ata RP AUDESP {self.numero_ata_registro_preco} ({self.ano_ata})"


class AudespEmpenhoContrato(models.Model):
    # Relacionamento com o modelo de ajuste/contrato, se o empenho for referente a um deles
    ajuste_contratual_audesp = models.ForeignKey(
        'AudespAjusteContratual', # Referência à Formalização de Ajuste Contratual
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='empenhos_audesp',
        verbose_name="Ajuste Contratual (AUDESP)",
        help_text="Ajuste/Formalização Contratual ao qual este empenho se refere."
    )
    # Opcional: Vínculo com o DocumentoFiscal (onde o empenho pode estar registrado no Financeiro)
    documento_fiscal_origem = models.ForeignKey(
        'financeiro.DocumentoFiscal',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='empenhos_audesp',
        verbose_name="Documento Fiscal de Origem",
        help_text="Documento fiscal original que registrou este empenho."
    )
    # Opcional: Vínculo com o processo principal, para rastreamento
    processo_vinculado = models.ForeignKey(
        Processo,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='empenhos_audesp',
        verbose_name="Processo Principal (SysGov)"
    )

    # --- Campos do 'descritor' no esquema de Empenho ---
    municipio = models.IntegerField(
        verbose_name="Município (Cód. AUDESP)"
    )
    entidade = models.IntegerField(
        verbose_name="Entidade (Cód. AUDESP)"
    )
    codigo_contrato_audesp = models.CharField(
        max_length=30,
        verbose_name="Código do Contrato (AUDESP)",
        help_text="Código único que identifica o ajuste (contrato) ao qual o empenho se refere."
    )
    retificacao = models.BooleanField(
        default=False,
        verbose_name="É Retificação (AUDESP)",
        help_text="True se o documento é uma retificação."
    )

    # --- Campos Principais do Esquema de Empenho ---
    numero_empenho = models.CharField(
        max_length=35,
        unique=True, # Número de empenho deve ser único
        verbose_name="Número do Empenho",
        help_text="Número do empenho no sistema de origem."
    )
    ano_empenho = models.IntegerField(
        verbose_name="Ano do Empenho"
    )
    data_emissao_empenho = models.DateField(
        verbose_name="Data de Emissão do Empenho"
    )

    # Outros campos internos de gestão
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_ultima_atualizacao = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Criado Por"
    )

    class Meta:
        verbose_name = "AUDESP Empenho de Contrato"
        verbose_name_plural = "AUDESP Empenhos de Contrato"
        ordering = ['-data_emissao_empenho']
        unique_together = ('municipio', 'entidade', 'numero_empenho', 'ano_empenho')

    def __str__(self):
        return f"Empenho AUDESP {self.numero_empenho}/{self.ano_empenho}"