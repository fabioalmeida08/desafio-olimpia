import feedparser
import requests
import wikipedia
import yfinance as yf
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun


@tool("buscar_nome_empresa")
def buscar_nome_empresa(empresa: str) -> str:
    """USE SEMPRE PRIMEIRO quando o nome fornecido for ambíguo, apelido ou incompleto.

    Retorna a razão social oficial da empresa brasileira usando busca no DuckDuckGo.
    Extraia o nome completo (ex: "Minerva S.A.", "Magazine Luiza S.A.").

    Exemplos:
    - "minerva" → "Minerva S.A."
    - "magalu" ou "magazine luiza" → "Magazine Luiza S.A."
    - "itau" → "Itaú Unibanco Holding S.A."

    Chame esta ferramenta antes de qualquer outra se houver dúvida sobre o nome oficial.
    """
    duck = DuckDuckGoSearchRun()
    query = f"razão social oficial empresa {empresa} Brasil"
    try:
        resultado = duck.run(query)
        return resultado
    except Exception as e:
        return f"Erro ao buscar nome oficial via DuckDuckGo: {str(e)}"


@tool("busca_ticker_duckduckgo")
def buscar_ticker_duckduckgo(empresa: str) -> str:
    """USE APENAS COMO RESERVA se 'buscar_ticker_empresa' falhar.

    Busca o ticker da empresa na B3 via DuckDuckGo como fallback.
    Menos precisa que a busca direta no Yahoo Finance.
    """
    duck = DuckDuckGoSearchRun()
    query = f"ticker {empresa} B3 site:yahoo.com OR site:statusinvest.com.br OR site:investing.com"
    try:
        resultado = duck.run(query)
        return resultado
    except Exception as e:
        return f"Erro ao buscar ticker via DuckDuckGo: {str(e)}"


@tool("buscar_ticker_empresa")
def buscar_ticker_empresa(empresa: str) -> str:
    """PRIORIDADE MÁXIMA: Use esta ferramenta para obter o ticker oficial da B3 (.SA).

    Busca diretamente no autocomplete do Yahoo Finance — é a mais precisa e rápida.
    Sempre prefira esta sobre 'buscar_ticker_duckduckgo'.

    Exemplos:
    - "petrobras" → "PETR4.SA"
    - "vale" → "VALE3.SA"
    - "minerva" → "BEEF3.SA"

    Retorna apenas o ticker ou mensagem clara se não encontrar.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {"q": empresa, "quotesCount": 15, "newsCount": 0}
        resp = requests.get(url, params=params, timeout=30, headers=headers).json()

        for item in resp.get("quotes", []):
            symbol = item.get("symbol", "")
            if symbol.endswith(".SA"):
                return symbol
        return f"Nenhum ticker .SA encontrado para '{empresa}'."
    except Exception as e:
        return f"Erro ao buscar ticker no Yahoo Finance: {str(e)}"


@tool("resumo_empresa")
def resumo_empresa(empresa: str) -> str:
    """Retorna resumo completo da empresa em português (Wikipédia).

    Use com a razão social oficial ou ticker para melhores resultados.
    Extrai automaticamente:
    - Setor de atuação
    - Breve histórico
    - Principais produtos/serviços

    Ideal para preencher o relatório principal.
    """
    try:
        wikipedia.set_lang("pt")
        return wikipedia.summary(empresa, sentences=6)
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            return wikipedia.summary(e.options[0], sentences=6)
        except:
            return (
                f"Múltiplas páginas encontradas para '{empresa}'. Use o nome completo."
            )
    except wikipedia.exceptions.PageError:
        return f"Nenhuma página Wikipédia encontrada para '{empresa}'."
    except Exception as e:
        return f"Erro ao buscar resumo: {str(e)}"


@tool("noticias_empresa")
def noticias_empresa(empresa: str) -> str:
    """Busca até 10 notícias recentes sobre a empresa (Google News Brasil).

    Use preferencialmente com a razão social oficial.
    Retorna título + link já formatados para o relatório.
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
    """Retorna o preço de fechamento mais recente da ação na B3 (em R$).

    USE APENAS com ticker válido (ex: "VALE3.SA", "PETR4.SA").
    Nunca passe nome da empresa aqui — só o código!
    """
    try:
        acao = yf.Ticker(ticker.upper())
        hist = acao.history(period="5d")
        if hist.empty:
            return f"Sem dados de preço para {ticker.upper()} (pode estar suspensa ou sem negociação recente)."
        preco = hist["Close"].iloc[-1]
        return f"{ticker.upper()} fechou em R$ {preco:.2f}"
    except Exception as e:
        return f"Erro ao obter preço de {ticker.upper()}: {str(e)}"


def get_tools():
    return [
        buscar_nome_empresa,
        buscar_ticker_empresa,
        resumo_empresa,
        preco_acao_empresa,
        noticias_empresa,
        buscar_ticker_duckduckgo,
    ]
