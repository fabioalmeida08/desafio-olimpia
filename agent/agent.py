from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from tools.finance_tools import get_tools
from utils.utils import clear_term, rich_print


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
        )
        self.empresa = empresa
        self.prompt = f"""Você é um analista financeiro que pesquisa empresas brasileiras automaticamente. 
Para a empresa fornecida '{self.empresa}', siga estes passos EXATAMENTE nesta ordem, 
SEM PERGUNTAR NADA AO USUÁRIO PARA CONFIRMAÇÃO — infira tudo usando as tools disponíveis:

## FLUXO DE EXECUÇÃO:

1. **Identificação da Razão Social**
   Se o nome parecer incompleto ou ambíguo (ex: apelido ou nome curto):
   - Chame 'resumo_empresa' (Wikipédia) e extraia o nome completo do resumo 
     (geralmente a primeira frase menciona a razão social)
   - Ou chame 'buscar_ticker_empresa' e use o ticker .SA mais relevante 
     para deduzir o nome oficial (o Yahoo retorna nomes associados)
   Assuma o resultado mais provável como razão social, sem hesitação.

2. **Coleta de Dados**
   Com a razão social identificada:
   - Obtenha o resumo da empresa (incluindo setor, histórico breve e produtos/serviços)
   - Descubra o ticker automaticamente
   - Obtenha até 3 notícias recentes, não repetidas, com título e link
   - Obtenha o preço da ação

3. **Formatação do Relatório**
   Formate o output como um relatório profissional em Markdown, seguindo EXATAMENTE esta estrutura:

# 📊 Relatório de Análise Financeira

**Empresa:** [Nome Completo]  

**Ticker:** [CÓDIGO.SA]  

---

## 🏢 Razão Social
[Nome oficial completo da empresa]

---

## 🏭 Setor de Atuação
[Setor principal e subsetor, se aplicável]

---

## 📜 Breve Histórico
[2-3 parágrafos sobre fundação, evolução e marcos importantes]

---

## 🎯 Principais Produtos/Serviços
[Lista dos produtos/serviços principais]

---

## 📰 Notícias Recentes

1. **[Título da Notícia 1]**  
   🔗 [Ler mais](URL)

2. **[Título da Notícia 2]**  
   🔗 [Ler mais](URL)

3. **[Título da Notícia 3]**  
   🔗 [Ler mais](URL)

---

## 💰 Preço Atual da Ação

**Cotação:** R$ [valor]

---

## REGRAS ABSOLUTAS:
1. NÃO PERGUNTE POR CONFIRMAÇÃO — prossiga sempre com a melhor inferência baseada nas tools
2. Se não encontrar alguma informação, use "[Informação não disponível]"
3. Certifique-se de que todos os emojis estejam em formato Unicode
4. Todos os links devem ser incluídos entre parênteses após 🔗 [Ler mais](URL)
5. O ticker DEVE terminar em ".SA"
6. O preço deve ser formatado como "R$ [valor]" com duas casas decimais

Execute agora para '{self.empresa}' e retorne apenas o relatório formatado."""

    def generate_report(self):
        clear_term()
        print("Gerando relatório... Por favor aguarde.")
        resposta = self.agent.invoke(
            {"messages": [{"role": "user", "content": self.prompt}]}
        )
        clear_term()
        rich_print(resposta["messages"][-1].content[0]["text"])
