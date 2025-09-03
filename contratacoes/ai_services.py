# SysGov_Project/contratacoes/ai_services.py

# --- ETAPA 1: IMPORTAÇÕES ESSENCIAIS ---
import google.generativeai as genai
from decouple import config
import re

# --- ETAPA 2: CONFIGURAÇÃO DA API KEY ---
GOOGLE_API_KEY = config('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


# --- FUNÇÃO 1: PARA GERAR O TEXTO COM A IA ---
def gerar_rascunho_etp_com_ia(descricao_necessidade):
    """
    Usa a IA para gerar um rascunho completo do ETP.
    """
    prompt = f"""
    Você é um especialista em licitações e contratos da administração pública brasileira.
    Sua tarefa é criar um rascunho detalhado para um Estudo Técnico Preliminar (ETP) com base na necessidade descrita.
    A resposta deve ser um texto claro e bem estruturado, dividido EXATAMENTE nas seções a seguir. Preencha cada seção da melhor forma possível.

    Necessidade Descrita pelo Usuário: "{descricao_necessidade}"

    --- Rascunho do ETP ---

    **TÍTULO SUGERIDO:**
    [Crie um título claro e objetivo para o ETP com base na necessidade]

    **SETOR DEMANDANTE SUGERIDO:**
    [Se a necessidade mencionar um setor (ex: saúde, educação), coloque-o aqui. Senão, deixe em branco.]

    **1. DESCRIÇÃO DA NECESSIDADE:**
    [Elabore aqui uma descrição formal da necessidade]

    **2. OBJETIVO DA CONTRATAÇÃO:**
    [Descreva aqui qual o resultado esperado com a contratação]

    **3. REQUISITOS DA CONTRATAÇÃO:**
    [Liste aqui os requisitos essenciais do objeto a ser contratado]

    **4. LEVANTAMENTO DE SOLUÇÕES DE MERCADO:**
    [Descreva brevemente as possíveis soluções que existem no mercado]

    **5. ESTIMATIVA DAS QUANTIDADES:**
    [Forneça uma estimativa inicial da quantidade necessária, justificando o cálculo]

    **6. ESTIMATIVA DO VALOR DA CONTRATAÇÃO (R$):**
    [Forneça uma estimativa de custo bem fundamentada, sugerindo fontes para pesquisa de preço. NÃO coloque um valor numérico final, apenas o texto da estimativa.]

    **7. RESULTADOS ESPERADOS:**
    [Detalhe os benefícios que a administração pública terá com esta contratação]

    **8. VIABILIDADE E JUSTIFICATIVA DA SOLUÇÃO ESCOLHIDA:**
    [Argumente por que a solução proposta é a mais viável para a administração]
    
    **10. ALINHAMENTO COM O PLANEJAMENTO ESTRATÉGICO:**
    [Elabore um texto justificando como esta contratação se alinha com objetivos maiores da instituição, como modernização, eficiência, melhoria de serviços públicos e valorização de servidores.]
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com o serviço de IA: {e}"


# --- FUNÇÃO 2: A NOVA FUNÇÃO PARSE QUE ESTÁ FALTANDO ---
def parse_rascunho_etp(rascunho_texto):
    """
    Recebe o texto bruto gerado pela IA e o transforma em um dicionário
    mapeado para os campos do modelo ETP.
    """
    dados_etp = {}
    padrao = r"\*\*(?:\d+\.\s*)?([^:]+):\*\*\s*(.*?)(?=\n\*\*\s*[\d\w]|\Z)"
    partes = re.findall(padrao, rascunho_texto, re.DOTALL)

    mapa_campos = {
        'TÍTULO SUGERIDO': 'titulo',
        'SETOR DEMANDANTE SUGERIDO': 'setor_demandante',
        'DESCRIÇÃO DA NECESSIDADE': 'descricao_necessidade',
        'OBJETIVO DA CONTRATAÇÃO': 'objetivo_contratacao',
        'REQUISITOS DA CONTRATAÇÃO': 'requisitos_contratacao',
        'LEVANTAMENTO DE SOLUÇÕES DE MERCADO': 'levantamento_solucoes_mercado',
        'ESTIMATIVA DAS QUANTIDADES': 'estimativa_quantidades',
        'ESTIMATIVA DO VALOR DA CONTRATAÇÃO (R$)': 'resultados_esperados',
        'RESULTADOS ESPERADOS': 'resultados_esperados',
        'VIABILIDADE E JUSTIFICATIVA DA SOLUÇÃO ESCOLHIDA': 'viabilidade_justificativa_solucao',
        'ALINHAMENTO COM O PLANEJAMENTO ESTRATÉGICO': 'alinhamento_planejamento',
    }

    for titulo, conteudo in partes:
        titulo_limpo = titulo.strip().upper()
        if titulo_limpo in mapa_campos:
            campo_modelo = mapa_campos[titulo_limpo]
            if campo_modelo not in dados_etp:
                dados_etp[campo_modelo] = conteudo.strip()

    return dados_etp


# SysGov_Project/contratacoes/ai_services.py

import google.generativeai as genai
from decouple import config
import re

# Configuração da API Key (continua igual)
GOOGLE_API_KEY = config('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# --- FUNÇÃO 1: GERAR RASCUNHO DO ETP (JÁ EXISTENTE) ---
def gerar_rascunho_etp_com_ia(descricao_necessidade):
    """
    Recebe a descrição da necessidade do usuário e usa a IA para gerar um
    rascunho estruturado para um Estudo Técnico Preliminar (ETP).
    """
    prompt = f"""
    Você é um especialista em licitações e contratos da administração pública brasileira.
    Sua tarefa é criar um rascunho detalhado para um Estudo Técnico Preliminar (ETP) com base na necessidade descrita.
    A resposta deve ser um texto claro e bem estruturado, dividido EXATAMENTE nas seções a seguir. Preencha cada seção da melhor forma possível.

    Necessidade Descrita pelo Usuário: "{descricao_necessidade}"

    --- Rascunho do ETP ---

    **TÍTULO SUGERIDO:**
    [Crie um título claro e objetivo para o ETP com base na necessidade]

    **SETOR DEMANDANTE SUGERIDO:**
    [Se a necessidade mencionar um setor (ex: saúde, educação), coloque-o aqui. Senão, deixe em branco.]

    **1. DESCRIÇÃO DA NECESSIDADE:**
    [Elabore aqui uma descrição formal da necessidade]

    **2. OBJETIVO DA CONTRATAÇÃO:**
    [Descreva aqui qual o resultado esperado com a contratação]

    **3. REQUISITOS DA CONTRATAÇÃO:**
    [Liste aqui os requisitos essenciais do objeto a ser contratado]

    **4. LEVANTAMENTO DE SOLUÇÕES DE MERCADO:**
    [Descreva brevemente as possíveis soluções que existem no mercado]

    **5. ESTIMATIVA DAS QUANTIDADES:**
    [Forneça uma estimativa inicial da quantidade necessária, justificando o cálculo]

    **6. ESTIMATIVA DO VALOR DA CONTRATAÇÃO (R$):**
    [Forneça uma estimativa de custo bem fundamentada, sugerindo fontes para pesquisa de preço.]

    **7. RESULTADOS ESPERADOS:**
    [Detalhe os benefícios que a administração pública terá com esta contratação]

    **8. VIABILIDADE E JUSTIFICATIVA DA SOLUÇÃO ESCOLHIDA:**
    [Argumente por que a solução proposta é a mais viável para a administração]
    
    **10. ALINHAMENTO COM O PLANEJAMENTO ESTRATÉGICO:**
    [Elabore um texto justificando como esta contratação se alinha com objetivos maiores da instituição.]
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com o serviço de IA: {e}"

# --- FUNÇÃO 2: PROCESSAR O RASCUNHO DO ETP (JÁ EXISTENTE) ---
def parse_rascunho_etp(rascunho_texto):
    """
    Recebe o texto bruto gerado pela IA e o transforma em um dicionário
    mapeado para os campos do modelo ETP.
    """
    dados_etp = {}
    padrao = r"\*\*(?:\d+\.\s*)?([^:]+):\*\*\s*(.*?)(?=\n\*\*\s*[\d\w]|\Z)"
    partes = re.findall(padrao, rascunho_texto, re.DOTALL)
    mapa_campos = {
        'TÍTULO SUGERIDO': 'titulo',
        'SETOR DEMANDANTE SUGERIDO': 'setor_demandante',
        'DESCRIÇÃO DA NECESSIDADE': 'descricao_necessidade',
        'OBJETIVO DA CONTRATAÇÃO': 'objetivo_contratacao',
        'REQUISITOS DA CONTRATAÇÃO': 'requisitos_contratacao',
        'LEVANTAMENTO DE SOLUÇÕES DE MERCADO': 'levantamento_solucoes_mercado',
        'ESTIMATIVA DAS QUANTIDADES': 'estimativa_quantidades',
        'ESTIMATIVA DO VALOR DA CONTRATAÇÃO (R$)': 'resultados_esperados',
        'RESULTADOS ESPERADOS': 'resultados_esperados',
        'VIABILIDADE E JUSTIFICATIVA DA SOLUÇÃO ESCOLHIDA': 'viabilidade_justificativa_solucao',
        'ALINHAMENTO COM O PLANEJAMENTO ESTRATÉGICO': 'alinhamento_planejamento',
    }
    for titulo, conteudo in partes:
        titulo_limpo = titulo.strip().upper()
        if titulo_limpo in mapa_campos:
            campo_modelo = mapa_campos[titulo_limpo]
            if campo_modelo not in dados_etp:
                dados_etp[campo_modelo] = conteudo.strip()
    return dados_etp

# --- FUNÇÃO 3: GERAR RASCUNHO DO TR (VERSÃO ATUALIZADA E MAIS COMPLETA) ---
def gerar_rascunho_tr_com_ia(texto_etp_aprovado):
    """
    Recebe o texto de um ETP aprovado e usa a IA para gerar um
    rascunho MUITO MAIS COMPLETO para um Termo de Referência (TR).
    """
    prompt = f"""
    Você é um especialista em licitações e contratos da administração pública brasileira.
    Sua tarefa é atuar como um analista de requerimentos e criar um rascunho detalhado para um Termo de Referência (TR) com base no Estudo Técnico Preliminar (ETP) que foi aprovado.

    A resposta deve ser um documento formal, claro e bem estruturado, dividido nas seções de um TR padrão. Use as informações do ETP abaixo para preencher cada seção da melhor forma possível. Para seções mais burocráticas (obrigações, sanções, fiscalização), gere um texto padrão e juridicamente sólido.

    --- ETP Aprovado (Fonte de Dados) ---
    {texto_etp_aprovado}
    --- Fim do ETP ---

    --- Rascunho do Termo de Referência (TR) ---

    **1. OBJETO:**
    [Com base no ETP, descreva de forma clara e concisa o que será contratado.]

    **2. JUSTIFICATIVA E OBJETIVOS DA CONTRATAÇÃO:**
    [Use a justificativa e os objetivos do ETP para elaborar este campo.]

    **3. ESPECIFICAÇÕES TÉCNICAS E REQUISITOS:**
    [Detalhe aqui as características técnicas, funcionais e de qualidade do bem ou serviço, usando os requisitos definidos no ETP como base.]
    
    **4. PRAZO DE EXECUÇÃO/ENTREGA:**
    [Sugira um prazo de entrega ou execução razoável para o objeto descrito.]

    **5. CRITÉRIOS DE ACEITAÇÃO DO OBJETO:**
    [Descreva como a administração irá verificar se o que foi entregue está de acordo com o que foi solicitado nas especificações.]

    **6. OBRIGAÇÕES DA CONTRATADA E DA CONTRATANTE:**
    [Gere um texto padrão com as principais obrigações de ambas as partes em um contrato público.]
    
    **7. SANÇÕES ADMINISTRATIVAS:**
    [Gere um texto padrão citando as possíveis sanções em caso de descumprimento contratual, com base na Lei 14.133/21.]
    
    **8. FISCALIZAÇÃO DO CONTRATO:**
    [Gere um texto padrão descrevendo o papel do fiscal do contrato e a forma como a fiscalização será conduzida.]
    
    **9. VIGÊNCIA DO CONTRATO:**
    [Sugira um prazo de vigência padrão para este tipo de contrato (ex: 12 meses).]
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com o serviço de IA: {e}"


# --- FUNÇÃO 4: PROCESSAR O RASCUNHO DO TR (VERSÃO ATUALIZADA) ---
def parse_rascunho_tr(rascunho_texto):
    """
    Recebe o texto bruto do TR gerado pela IA e o transforma num dicionário
    mapeado para os campos do modelo TR.
    """
    dados_tr = {}
    padrao = r"\*\*(?:\d+\.\s*)?([^:]+):\*\*\s*(.*?)(?=\n\*\*\d+\.|\Z)"
    partes = re.findall(padrao, rascunho_texto, re.DOTALL)

    # MAPA DE CAMPOS ATUALIZADO PARA INCLUIR AS NOVAS SEÇÕES
    mapa_campos = {
        'OBJETO': 'objeto',
        'JUSTIFICATIVA E OBJETIVOS DA CONTRATAÇÃO': 'justificativa',
        'ESPECIFICAÇÕES TÉCNICAS E REQUISITOS': 'especificacoes_tecnicas',
        'PRAZO DE EXECUÇÃO/ENTREGA': 'prazo_execucao_entrega',
        'CRITÉRIOS DE ACEITAÇÃO DO OBJETO': 'criterios_aceitacao',
        'OBRIGAÇÕES DA CONTRATADA E DA CONTRATANTE': 'obrigacoes_partes',
        'SANÇÕES ADMINISTRATIVAS': 'sancoes_administrativas',
        'FISCALIZAÇÃO DO CONTRATO': 'fiscalizacao_contrato',
        'VIGÊNCIA DO CONTRATO': 'vigencia_contrato',
    }

    for titulo, conteudo in partes:
        titulo_limpo = titulo.strip().upper()
        if titulo_limpo in mapa_campos:
            campo_modelo = mapa_campos[titulo_limpo]
            dados_tr[campo_modelo] = conteudo.strip()

    return dados_tr


# Em contratacoes/ai_services.py

# ... (suas outras funções de IA continuam aqui em cima) ...

# --- NOVA FUNÇÃO 4: PROCESSAR O RASCUNHO DO TR ---
def parse_rascunho_tr(rascunho_texto):
    """
    Recebe o texto bruto do TR gerado pela IA e o transforma num dicionário
    mapeado para os campos do modelo TR.
    """
    dados_tr = {}
    padrao = r"\*\*(?:\d+\.\s*)?([^:]+):\*\*\s*(.*?)(?=\n\*\*\d+\.|\Z)"
    partes = re.findall(padrao, rascunho_texto, re.DOTALL)

    # Mapeia os títulos do rascunho para os campos do nosso modelo TR
    mapa_campos = {
        'OBJETO': 'objeto',
        'JUSTIFICATIVA E OBJETIVOS DA CONTRATAÇÃO': 'justificativa',
        'ESPECIFICAÇÕES TÉCNICAS E REQUISITOS': 'especificacoes_tecnicas',
        'PRAZOS E CONDIÇÕES DE ENTREGA/EXECUÇÃO': 'prazo_execucao_entrega',
        'CRITÉRIOS DE ACEITAÇÃO DO OBJETO': 'criterios_aceitacao',
    }

    for titulo, conteudo in partes:
        titulo_limpo = titulo.strip().upper()
        if titulo_limpo in mapa_campos:
            campo_modelo = mapa_campos[titulo_limpo]
            dados_tr[campo_modelo] = conteudo.strip()

    return dados_tr

