from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.structured_output import ToolStrategy

from tools.finance_tools import get_tools
from utils.utils import clear_term
from dataclasses import asdict, dataclass
from typing import Optional, List
import json

@dataclass
class NewsItem:
    title: str
    link: str

@dataclass
class ResponseFormat:
    """Esquema de resposta para o agente."""
    nome_empresa: str
    resumo_empresa: str
    preco_acao: Optional[float]
    moeda: Optional[str] = "BRL"
    noticias: Optional[List[NewsItem]] = None

    def to_json(self):
        return json.dumps(asdict(self), indent = 2 ,ensure_ascii=False)

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
            response_format=ToolStrategy(ResponseFormat)
        )
        self.empresa = empresa
        self.prompt = f"""
        Você é um analista financeiro que pesquisa empresas brasileiras automaticamente. Para a empresa fornecida '{self.empresa}', siga estes passos EXATAMENTE nesta ordem, SEM PERGUNTAR NADA AO USUÁRIO PARA CONFIRMAÇÃO — infira tudo usando as tools disponíveis:

        1. Se o nome parecer incompleto ou ambíguo (ex: apelido ou nome curto), use a tool 'resumo_empresa' (Wikipédia) ou 'buscar_ticker_duckduckgo' para inferir a razão social oficial. Por exemplo:
           - Chame resumo_empresa com o nome fornecido e extraia o nome completo do resumo (geralmente a primeira frase menciona a razão social).
           - Ou chame buscar_ticker_duckduckgo e use o ticker .SA mais relevante para deduzir o nome oficial , se falhar tente usar o buscar_ticker_empresa (o Yahoo retorna nomes associados).
           Assuma o resultado mais provável como razão social, sem hesitação.

        2. Com a razão social inferida, use as tools para:
           - Obter o resumo da empresa (incluindo setor, histórico breve e produtos/serviços).
           - Descobrir o ticker automaticamente.
           - Obter até 3 notícias recentes, não repetidas, com título e link.
           - Obter o preço da ação.

        3. Formate o output para ficar de acordo com o ResponseFormat includindo:
           - Razão Social da Empresa
           - Setor de Atuação
           - Breve Histórico
           - Principais Produtos/Serviços
           - 3 Notícias Recentes (com links)
           - Preço Atual da Ação

        NÃO PERGUNTE POR CONFIRMAÇÃO — prossiga sempre com a melhor inferência baseada nas tools. Se não encontrar, reporte o erro sem interagir.
        """

    def generate_report(self):
        clear_term()
        print("Interagindo com llm... Por favor aguarde.")
        resposta = self.agent.invoke(
            {"messages": [{"role": "user", "content": self.prompt}]}
        )
        clear_term()
        print(resposta["structured_response"].to_json())
