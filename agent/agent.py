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
    def generate_report(self):
        clear_term()
        print("Gerando relatório... Por favor aguarde.")
        resposta = self.agent.invoke(
            {"messages": [{"role": "user", "content": self.prompt}]}
        )
        clear_term()
        rich_print(resposta["messages"][-1].content)
