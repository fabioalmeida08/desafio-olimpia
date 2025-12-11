import os
import platform

from dotenv import load_dotenv

from rich.console import Console
from rich.markdown import Markdown

def rich_print(report: str):
    console = Console()

    md = Markdown(f"""{report}""")
    console.print(md)

from dotenv import load_dotenv

def load_api_key():
    load_dotenv()
    api_key = os.getenv("API_KEY")

    if not api_key:
        print("\n⚠️  API Key do Gemini não encontrada!")
        print("\n📝 Como obter gratuitamente:")
        print("   1. Acesse: https://aistudio.google.com/app/apikey")
        print("   2. Clique em 'Create API Key'")
        print("   3. Copie a chave")
        print("\n💡 Depois, crie um arquivo .env com:")
        print("   API_KEY=sua_chave_aqui\n")
        api_key = input("Ou cole sua API Key aqui (ou Enter para sair): ").strip()
        if not api_key:
            raise SystemExit("Saindo... API Key não fornecida.")
        else:
            return api_key
    return api_key


def clear_term():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
