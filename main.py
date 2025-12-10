from utils import load_api_key
from langchain.tools import tool
import requests
import feedparser
import yfinance as yf
import wikipedia

if __name__ == "__main__":
    load_api_key()

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
