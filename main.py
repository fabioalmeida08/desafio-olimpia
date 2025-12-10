import feedparser
import requests
import wikipedia
import yfinance as yf
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from utils import load_api_key

if __name__ == "__main__":
    api_key = load_api_key()

    @tool
    def tool_buscar_ticker(empresa: str) -> str:
        """
        Busca automaticamente o ticker da empresa usando o autocomplete
        do Yahoo Finance, priorizando tickers da B3 (.SA).
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {"q": empresa, "quotesCount": 10}

            resp = requests.get(url, params=params, timeout=20, headers=headers).json()

            for item in resp.get("quotes", []):
                symbol = item.get("symbol", "")
                if symbol.endswith(".SA"):
                    return symbol

            return f"Nenhum ticker da B3 encontrado para '{empresa}'."

        except Exception as e:
            return f"Erro ao buscar ticker: {str(e)}"

    @tool
    def tool_resumo(empresa: str) -> str:
        """
        Busca um resumo curto da empresa na Wikipédia.
        - Wikipedia tem informações rápidas, gratuitas e confiáveis.
        """
        try:
            wikipedia.set_lang("pt")
            return wikipedia.summary(empresa, sentences=3)
        except:
            return f"Nenhum resumo encontrado para {empresa}."

    @tool
    def tool_noticias(empresa: str) -> str:
        """
        Coleta 2-3 notícias recentes usando Google News RSS.
        - feedparser interpreta RSS facilmente.
        """
        query = empresa.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

        feed = feedparser.parse(url)

        noticias = []
        for item in feed.entries[:20]:
            noticias.append(f"- {item.title}\n  {item.link}")

        if not noticias:
            return "Nenhuma notícia encontrada."

        return "\n".join(noticias)

    @tool
    def tool_preco_acao(ticker: str) -> str:
        """
        Usa yfinance para obter o fechamento mais recente.
        - Yahoo Finance suporta empresas brasileiras (.SA)
        """

        ticker = ticker
        acao = yf.Ticker(ticker)
        hist = acao.history(period="1d")

        if hist.empty:
            return "Preço não encontrado."

        preco = hist["Close"].iloc[0]
        return f"{ticker} fechou em R$ {preco:.2f}"

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.2,
        google_api_key=api_key,
    )

    tools = [tool_preco_acao, tool_resumo, tool_noticias, tool_buscar_ticker]

    agent = create_agent(
        llm,
        tools,
    )

    empresa = input("Digite o nome da empresa: ")

    prompt = f"""
    Você é um analista financeiro que pesquisa empresas brasileiras automaticamente. Para a empresa fornecida '{empresa}', siga estes passos EXATAMENTE nesta ordem, SEM PERGUNTAR NADA AO USUÁRIO PARA CONFIRMAÇÃO — infira tudo usando as tools disponíveis:

    1. Se o nome parecer incompleto ou ambíguo (ex: apelido ou nome curto), use a tool 'tool_resumo' (Wikipédia) ou 'tool_buscar_ticker' (Yahoo Finance) para inferir a razão social oficial. Por exemplo:
       - Chame tool_resumo com o nome fornecido e extraia o nome completo do resumo (geralmente a primeira frase menciona a razão social).
       - Ou chame tool_buscar_ticker e use o ticker .SA mais relevante para deduzir o nome oficial (o Yahoo retorna nomes associados).
       Assuma o resultado mais provável como razão social, sem hesitação.

    2. Com a razão social inferida, use as tools para:
       - Obter o resumo da empresa (incluindo setor, histórico breve e produtos/serviços).
       - Descobrir o ticker automaticamente.
       - Obter até 3 notícias recentes, não repetidas, com título e link.
       - Obter o preço da ação.

    3. Formate o output como um relatório profissional, bem espaçado, com seções claras e emojis. O relatório deve incluir:
       - Razão Social da Empresa
       - Setor de Atuação
       - Breve Histórico
       - Principais Produtos/Serviços
       - 3 Notícias Recentes (com links)
       - Preço Atual da Ação
       Use formatação em texto simples que será exibido em um terminal como bash, com linhas separadoras e emojis.

    NÃO PERGUNTE POR CONFIRMAÇÃO — prossiga sempre com a melhor inferência baseada nas tools. Se não encontrar, reporte o erro sem interagir.
    """

    print("\nGerando relatório... Aguarde uns segundos\n")

    resposta = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    print(resposta["messages"][-1].content)
