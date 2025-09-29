import re
from typing import List, NamedTuple, Optional


class Token(NamedTuple):
    type: str
    value: str
    line: int = 1
    column: int = 1


# Palavras-chave do Quokka 
KEYWORDS = {
    # Estruturas principais
    "global", "main", "fun",
    # Controle de fluxo
    "if", "else", "while", "each", "break", "continue", "exit",
    # Valores especiais
    "true", "false", "null",
    # Operações especiais
    "yield", "print", "next", "prompt"
}


# Símbolos e operadores do Quokka
SYMBOLS = {
    # Delimitadores
    "{", "}", "(", ")", "[", "]",
    # Operadores aritméticos
    "+", "-", "*", "/", "+=", "-=", "<<", "++", "--", "**", "%"
    # Operadores de comparação
    "==", "!=", ">=", "<=", ">", "<",
    # Operadores lógicos
    "&&", "||",
    # Outros símbolos
    "=", ".", ":", "$", ","
}


# Regex para tokenização - ordem importa!
TOKEN_PATTERNS = [
    (r'#.*', 'COMMENT'),                    # Comentários (se houver)
    (r'"(?:[^"\\]|\\.)*"', 'STRING'),       # Strings com aspas duplas
    (r"'(?:[^'\\]|\\.)*'", 'KEY'),          # Keys com aspas simples
    (r'-?\d+\.\d+', 'FLOAT'),                # Números decimais (incluindo negativos)
    (r'-?\d+', 'INT'),                      # Números inteiros (incluindo negativos)
    (r'==|!=|>=|<=|&&|\|\||\+\+|\-\-|\+=|\-=|<<|\*\*', 'DOPERATOR'),   # Operadores de 2 caracteres
    (r'[{}()\[\],]', 'SYMBOL'),             # Símbolos de 1 caractere
    (r'[.=:+\-*/><!$%]', 'OOPERATOR'),      # Operadores de 1 caractere
    (r'[a-zA-Z_][a-zA-Z0-9_.]*', 'WORD'),  # Identificadores e palavras-chave
    (r'\s+', 'WHITESPACE'),                 # Espaços em branco
    (r'.', 'UNKNOWN')                       # Qualquer outro caractere
]


class QuokkaLexer:
    def __init__(self):
        # Compila todos os padrões em uma única regex
        self.token_regex = '|'.join(f'({pattern})' for pattern, _ in TOKEN_PATTERNS)
        self.pattern_types = [token_type for _, token_type in TOKEN_PATTERNS]
   
    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        line = 1
        column = 1
       
        for match in re.finditer(self.token_regex, code):
            token_value = match.group()
           
            # Descobre qual padrão foi encontrado
            token_type = None
            for i, group in enumerate(match.groups()):
                if group is not None:
                    token_type = self.pattern_types[i]
                    break
           
            # Pula espaços em branco e comentários
            if token_type in ['WHITESPACE', 'COMMENT']:
                if '\n' in token_value:
                    line += token_value.count('\n')
                    column = len(token_value) - token_value.rfind('\n')
                else:
                    column += len(token_value)
                continue
           
            # Classifica o token mais especificamente
            final_type = self._classify_token(token_type, token_value)
           
            # Remove aspas das strings e keys
            if final_type == 'STRING':
                token_value = self._process_string(token_value)
            elif final_type == 'KEY':
                token_value = self._process_key(token_value)
           
            tokens.append(Token(final_type, token_value, line, column))
            column += len(match.group())
       
        return tokens
   
    def _classify_token(self, token_type: str, value: str) -> str:
        """Classifica o token mais especificamente"""
        if token_type == 'WORD':
            if value in KEYWORDS:
                return 'KEYWORD'
            else:
                return 'IDENTIFIER'
        elif token_type == 'SYMBOL':
            if value in SYMBOLS:
                return 'SYMBOL'
            else:
                return 'UNKNOWN'
        else:
            return token_type
   
    def _process_string(self, value: str) -> str:
        """Remove aspas e processa escapes em strings"""
        content = value[1:-1]  # Remove aspas
        # Processa escapes básicos
        content = content.replace('\\"', '"')
        content = content.replace('\\\\', '\\')
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '\t')
        return content
   
    def _process_key(self, value: str) -> str:
        """Remove aspas de keys"""
        return value[1:-1]  # Remove aspas simples


# Função auxiliar para debug
def print_tokens(tokens: List[Token], show_position: bool = False):
    """Imprime os tokens de forma organizada"""
    print("TIPO         | VALOR           | POSIÇÃO")
    print("-" * 45)
    for token in tokens:
        pos_info = f"L{token.line:2}C{token.column:2}" if show_position else ""
        print(f"{token.type:12} | {str(token.value):15} | {pos_info}")


# Teste básico
if __name__ == "__main__":
    # Exemplo de código Quokka
    test_code = '''
    
    prompt("qual é seu nome?")
    '''
   
    lexer = QuokkaLexer()
    tokens = lexer.tokenize(test_code)
   
    print("=== TOKENS GERADOS ===")
    print_tokens(tokens, show_position=True) 