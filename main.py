from agent.agent import FinanceAgent
from utils.utils import load_api_key, clear_term

if __name__ == "__main__":
    api_key = load_api_key()

    clear_term()

    empresa = input("Digite o nome da empresa: ")

    if not empresa:
        raise Exception("Digite um nome valido para empresa")

    agent = FinanceAgent(api_key, empresa)
    agent.generate_report()
