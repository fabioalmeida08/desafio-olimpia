import feedparser
import requests
import wikipedia
import yfinance as yf
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun 
import re


@tool("buscar_nome_empresa")
def buscar_nome_empresa(empresa: str) -> str:
    """
    Retorna o nome oficial da empresa usando DuckDuckGo.
    A extração do nome é feita pelo LLM.
    """
    duck = DuckDuckGoSearchRun()

    query = f"empresa {empresa} nome oficial"
    resultado = duck.run(query)
    return resultado

@tool("buscar_ticker_duckduckgo")
def buscar_ticker_duckduckgo(empresa: str) -> str:
    """
    Usa DuckDuckGo Search para tentar identificar o ticker da empresa na B3.
    Procura por tickers com final .SA (padrão do Yahoo Finance).
    """
    duck = DuckDuckGoSearchRun()

    query = f"ticker da empresa {empresa} B3 .SA código ação"

    try:
        resultado = duck.run(query)

        tickers = re.findall(r"\b[A-Z]{4}\d{1}\.SA\b", resultado)

        if tickers:
            return tickers[0]

        return f"Nenhum ticker encontrado para '{empresa}' via DuckDuckGo."

    except Exception as e:
        return f"Erro ao buscar via DuckDuckGo: {str(e)}"

@tool("buscar_ticker_empresa")
def buscar_ticker_empresa(empresa: str) -> str:
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

@tool("resumo_empresa")
def resumo_empresa(empresa: str) -> str:
    """
    Busca um resumo curto da empresa na Wikipédia.
    """
    try:
        wikipedia.set_lang("pt")
        return wikipedia.summary(empresa, sentences=3)
    except:
        return f"Nenhum resumo encontrado para {empresa}."

@tool("noticias_empresa")
def noticias_empresa(empresa: str) -> str:
    """
    Coleta notícias recentes usando Google News RSS.
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

@tool("preco_acao_empresa")
def preco_acao_empresa(ticker: str) -> str:
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

def get_tools():
    return [
        buscar_nome_empresa,
        buscar_ticker_duckduckgo,
        buscar_ticker_empresa,
        resumo_empresa,
        noticias_empresa,
        preco_acao_empresa,
    ]

