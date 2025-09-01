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