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
            model="gemini-2.5-flash",
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
Você é um analista financeiro que precisa preencher um objeto ResponseFormat 
com informações sobre a empresa informada: "{self.empresa}".

Siga exatamente este procedimento:

1. Identificação da empresa:
   - Se o nome estiver incompleto ou ambíguo, use as ferramentas para identificar
     a razão social correta:
        1) resumo_empresa  → extrair o nome oficial da primeira frase
        2) buscar_ticker_duckduckgo → usar o ticker .SA para deduzir o nome
        3) buscar_ticker_empresa → fallback
   - Escolha o nome mais provável com base nas tools. Nunca pergunte ao usuário.

2. Coleta de dados:
   - nome_empresa → razão social final encontrada
   - resumo_empresa → setor, histórico, produtos/serviços
   - preco_acao → obter com preco_acao_empresa (BRL)
   - noticias → obter no máximo 3 itens por noticias_empresa (título + link)

3. Regras:
   - Sempre use tools; nunca invente informações.
   - Sempre preencha todos os campos possíveis do ResponseFormat.
   - Se algo não for encontrado, deixe o campo como None.
   - Nunca gere texto fora da estrutura do ResponseFormat.
        """

    def generate_report(self):
        clear_term()
        print("Interagindo com llm... Por favor aguarde.")
        resposta = self.agent.invoke(
            {"messages": [{"role": "user", "content": self.prompt}]}
        )
        clear_term()
        print(resposta["structured_response"].to_json())
