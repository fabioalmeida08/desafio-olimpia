from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools.finance_tools import get_tools
from utils.utils import clear_term, rich_print


class FinanceAgent:
    def __init__(self, api_key: str, empresa: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.2,
            google_api_key=api_key,
        )
        self.tools = get_tools()
        self.agent = create_agent(
            self.llm,
            self.tools,
        )
        self.empresa = empresa
        self.prompt=f"""
Você é um analista financeiro automatizado especializado em empresas brasileiras. 
Para a empresa fornecida '{self.empresa}', siga rigorosamente as instruções abaixo, 
SEM pedir confirmação ao usuário. Sempre infira a melhor resposta usando as tools disponíveis.

1. Identificação da Razão Social
   - Caso o nome da empresa esteja incompleto, abreviado ou ambíguo, use as ferramentas nesta ordem:
       1. buscar_nome_empresa
       2. resumo_empresa (Wikipédia) — extraia o nome completo da primeira frase do resumo
       3. buscar_ticker_duckduckgo — use o ticker .SA mais relevante para deduzir o nome oficial
       4. buscar_ticker_empresa — fallback final para descobrir um ticker associado
   - Sempre selecione a razão social mais provável, sem hesitação.

2. Coleta de Informações da Empresa
   Com a razão social identificada:
   - Obtenha o resumo corporativo (setor, histórico breve, produtos/serviços).
   - Identifique o ticker da empresa usando:
       • buscar_ticker_duckduckgo
       • se falhar, usar buscar_ticker_empresa
     (garanta que o ticker final termine em .SA)
   - Reúna até 3 notícias recentes, sem duplicadas, incluindo título e link.
   - Obtenha o preço atual da ação.

3. Geração do Relatório Final
   Formate o resultado como um relatório profissional em Markdown, 
   bem espaçado e com seções claras.  
   Regras de formatação:
   - O título de cada seção deve começar com um emoji em formato Unicode, alinhado à esquerda.
   - Utilize divisores e espaçamento adequado.
   - Inclua todos os links das notícias.

   O relatório deve conter:
     • Razão Social da Empresa  
     • Setor de Atuação  
     • Breve Histórico  
     • Principais Produtos/Serviços  
     • 3 Notícias Recentes (com links)  
     • Preço Atual da Ação  

4. Comportamento
   - NÃO pergunte nada ao usuário.  
   - Sempre siga o fluxo decisório automaticamente.  
   - Se alguma etapa falhar, retorne um erro informativo sem solicitar interação.  
   - Garanta que todos os emojis estejam em Unicode. 
        """
        # self.prompt = f"""
        # Você é um analista financeiro que pesquisa empresas brasileiras automaticamente. Para a empresa fornecida '{self.empresa}', siga estes passos EXATAMENTE nesta ordem, SEM PERGUNTAR NADA AO USUÁRIO PARA CONFIRMAÇÃO — infira tudo usando as tools disponíveis:
        #
        # 1. Se o nome parecer incompleto ou ambíguo (ex: apelido ou nome curto), use a tool buscar_nome_empresa e se falhar tente usar a tool 'resumo_empresa' (Wikipédia) ou 'buscar_ticker_duckduckgo'. Por exemplo:
        #    - Tente achar o nome da empresa com buscar_nome_empresa caso não ache tente hame resumo_empresa com o nome fornecido e extraia o nome completo do resumo (geralmente a primeira frase menciona a razão social).
        #    - Ou chame buscar_ticker_duckduckgo e use o ticker .SA mais relevante para deduzir o nome oficial (o Yahoo retorna nomes associados), caso falhe tente com buscar_ticker_empresa.
        #    Assuma o resultado mais provável como razão social, sem hesitação.
        #
        # 2. Com a razão social inferida, use as tools para:
        #    - Obter o resumo da empresa (incluindo setor, histórico breve e produtos/serviços).
        #    - Descobrir o ticker usando 'buscar_ticker_duckduckgo' caso não retorne resultado usar  'buscar_ticker_empresa'.
        #    - Obter até 3 notícias recentes, não repetidas, com título e link.
        #    - Obter o preço da ação.
        #
        # 3. Formate o output como um relatório profissional, bem espaçado, com seções claras usando emojis e linhas no formato Markdown, aonde os emojis (no formato unicode) fiquem no lado esquerdo e logo em seguida o titulo das seções de forma alinhada a esquerda.
        # O relatório deve incluir:
        #    - Razão Social da Empresa
        #    - Setor de Atuação
        #    - Breve Histórico
        #    - Principais Produtos/Serviços
        #    - 3 Notícias Recentes
        #    - Preço Atual da Ação
        #
        # NÃO PERGUNTE POR CONFIRMAÇÃO — prossiga sempre com a melhor inferência baseada nas tools. Se não encontrar, reporte o erro sem interagir.
        # NÃO SE ESQUEÇA DE ADICIONAR OS LINKS DAS NOTÍCIAS E SE CERTIFIQUE QUE OS EMOTES ESTÃO FORMATADOS COMO UNICODE.
        # """

    def generate_report(self):
        clear_term()
        print("Gerando relatório... Por favor aguarde.")
        resposta = self.agent.invoke(
            {"messages": [{"role": "user", "content": self.prompt}]}
        )
        clear_term()
        rich_print(resposta["messages"][-1].content)
