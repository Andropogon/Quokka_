import sys
from lexer import QuokkaLexer
from interpreter import QuokkaInterpreter

if __name__ == "__main__":
    # Verifica se o usuário passou um argumento
    if len(sys.argv) < 2:
        print("Uso: python main.py arquivo.qk")
        sys.exit(1)

    arquivo_qk = sys.argv[1]

    try:
        with open(arquivo_qk, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Erro: arquivo '{arquivo_qk}' não encontrado.")
        sys.exit(1)

    print("=== INTERPRETADOR QUOKKA ===")
    print(f"Executando '{arquivo_qk}'...\n")

    # Cria o interpretador e executa
    interpreter = QuokkaInterpreter()
    interpreter.interpret(code)

    print("\n=== EXECUÇÃO FINALIZADA ===") 