from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import sys

from lexer import QuokkaLexer, Token

class QuokkaArray:
    """Representa um array do Quokka (lista com sintaxe especial)"""
    def __init__(self, items: List[Any] = None):
        self.items = items or []
    
    def __str__(self):
        return "{ " + " . ".join(str(item) for item in self.items) + " }"
    
    def __repr__(self):
        return f"QuokkaArray({self.items})"
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, index):
        if isinstance(index, int) and 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def __setitem__(self, index, value):
        if isinstance(index, int):
            # Expande o array se necessário
            while len(self.items) <= index:
                self.items.append(None)
            self.items[index] = value
    
    def append(self, value):
        self.items.append(value)
    
    def to_list(self):
        return self.items.copy()

    def extend(self, other_array):
        """Adiciona todos os elementos de outro array"""
        if isinstance(other_array, QuokkaArray):
            self.items.extend(other_array.items)
        elif isinstance(other_array, list):
            self.items.extend(other_array)
        else:
            raise ValueError("extend() requer um QuokkaArray ou lista")

    def size(self):
        """Retorna o tamanho do array"""
        return len(self.items)

class QuokkaDict:
    """Representa um dicionário do Quokka"""
    def __init__(self, items: Dict[str, Any] = None):
        self.items = items or {}
    
    def __str__(self):
        pairs = []
        for key, value in self.items.items():
            if isinstance(value, str):
                value_str = f'"{value}"'
            else:
                value_str = str(value)
            pairs.append(f"'{key}' = {value_str}")
        return "{ " + " . ".join(pairs) + " }"
    
    def __repr__(self):
        return f"QuokkaDict({self.items})"
    
    def __getitem__(self, key):
        return self.items.get(str(key))
    
    def __setitem__(self, key, value):
        self.items[str(key)] = value
    
    def __contains__(self, key):
        return str(key) in self.items
    
    def keys(self):
        return list(self.items.keys())
    
    def values(self):
        return list(self.items.values())

    def update(self, other_dict):
        """Atualiza o dicionário com chaves de outro dicionário"""
        if isinstance(other_dict, QuokkaDict):
            self.items.update(other_dict.items)
        elif isinstance(other_dict, dict):
            self.items.update(other_dict)
        else:
            raise ValueError("update() requer um QuokkaDict ou dict")

    def size(self):
        """Retorna o número de chaves no dicionário"""
        return len(self.items)
# Tipos de dados que o Quokka pode ter
QuokkaValue = Union[None, bool, int, float, str, QuokkaArray, QuokkaDict]

@dataclass
class QuokkaError(Exception):
    """Erro customizado para o interpretador Quokka"""
    message: str
    line: int = 0
    column: int = 0

class BreakException(Exception):
    """Exceção especial para implementar break (controle de fluxo)"""
    pass

class ContinueException(Exception):
    """Exceção especial para implementar continue (controle de fluxo)"""
    pass

class Environment:
    """Ambiente de execução - armazena variáveis e seus valores"""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.variables: Dict[str, QuokkaValue] = {}
        self.parent = parent
    
    def define(self, name: str, value: QuokkaValue):
        """Define uma nova variável"""
        self.variables[name] = value
    
    def get(self, name: str) -> QuokkaValue:
        """Busca o valor de uma variável"""
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise QuokkaError(f"Variável '{name}' não definida")
    
    def set(self, name: str, value: QuokkaValue):
        """Atualiza o valor de uma variável existente"""
        if name in self.variables:
            self.variables[name] = value
        elif self.parent and self.parent.has(name):
            self.parent.set(name, value)
        else:
            # Se não existe, cria nova
            self.variables[name] = value
    
    def has(self, name: str) -> bool:
        """Verifica se uma variável existe"""
        return name in self.variables or (self.parent and self.parent.has(name))
    def create_local_scope(self) -> 'Environment':
        """Cria um novo escopo local baseado no atual"""
        return Environment(parent=self)

    def get_all_variables(self) -> Dict[str, QuokkaValue]:
        """Retorna todas as variáveis visíveis (incluindo do parent)"""
        all_vars = {}
        if self.parent:
            all_vars.update(self.parent.get_all_variables())
        all_vars.update(self.variables)
        return all_vars

class QuokkaFunction:
    """Representa uma função definida pelo usuário"""
    def __init__(self, name: str, params: List[str], body: List[Token], start_token: int, end_token: int):
        self.name = name
        self.params = params
        self.body = body  
        self.start_token = start_token  
        self.end_token = end_token      

class YieldException(Exception):
    """Exceção especial para implementar yield (controle de fluxo)"""
    def __init__(self, value):
        self.value = value

class QuokkaInterpreter:
    """Interpretador principal do Quokka"""
    def _execute_with_local_scope(self, execution_func, context="local"):
        """
    Executa uma função com escopo local temporário
    Garante que o escopo seja restaurado mesmo se houver erro
    """
    # Salva escopo atual
        old_env = self.current_env
    
        try:
        # Cria novo escopo local
            local_env = old_env.create_local_scope()
            self.current_env = local_env
        
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] Criando escopo local para: {context}")
        
        # Executa a função passada
            return execution_func()
        
        finally:
        # Sempre restaura o escopo original
            self.current_env = old_env
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] Escopo local restaurado: {context}")
    def enable_debug_mode(self):
        """Ativa modo debug para visualizar escopos"""
        self.debug_mode = True

    def disable_debug_mode(self):
        """Desativa modo debug"""
        self.debug_mode = False

    def _print_current_scope(self, context: str = ""):
        """Imprime o escopo atual (apenas se debug ativo)"""
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"[SCOPE {context}] Variáveis visíveis:")
            vars_dict = self.current_env.get_all_variables()
            for name, value in vars_dict.items():
                print(f"  {name} = {self._quokka_to_string(value)}")
            print()
    def __init__(self):
        self.lexer = QuokkaLexer()
        self.tokens: List[Token] = []
        self.current = 0
        
        # Ambientes de execução
        self.global_env = Environment()
        self.current_env = self.global_env
        
        # Armazena funções definidas pelo usuário
        self.functions: Dict[str, 'FunctionDef'] = {}
    
    def interpret(self, code: str):
        """Interpreta um código Quokka completo"""
        try:
            # Fase 1: Tokenização
            self.tokens = self.lexer.tokenize(code)
            self.current = 0
            
            # Fase 2: Análise e execução
            self._parse_program()
            
        except QuokkaError as e:
            print(f"ERRO: {e.message}")
            if e.line > 0:
                print(f"Linha: {e.line}, Coluna: {e.column}")
        except Exception as e:
            print(f"ERRO INTERNO: {e}")
    
    def _parse_function(self):
        """Analisa definição de função"""
        self._consume_keyword("fun")
    
    # Nome da função (pode ter pontos: calcular.imc)
        if not self._check_type("IDENTIFIER"):
            raise QuokkaError("Esperado nome da função")
    
        func_name = self._advance().value
    
    # Suporte para nomes com pontos (calcular.imc)
        while self._check_ooperator("."):
            self._advance()  # consome '.'
            if not self._check_type("IDENTIFIER"):
                raise QuokkaError("Esperado nome após '.' em função")
            func_name += "." + self._advance().value
    
    # Parâmetros da função
        self._consume_symbol("(")
    
        params = []
        if not self._check_symbol(")"): 
            while True:  
                if not self._check_type("IDENTIFIER"):
                    raise QuokkaError("Esperado nome do parâmetro")
            
                params.append(self._advance().value)
            
            
                if self._check_symbol(","):
                    self._advance()  
                    continue 
                elif self._check_symbol(")"):
                    break  
                else:
                    raise QuokkaError("Esperado ',' ou ')' em parâmetros")
    
        self._consume_symbol(")")
    
    # Marca início do corpo da função
        self._consume_symbol("{")
        start_token = self.current
    
    # Pula o corpo da função para analisar depois
        brace_count = 1
        while brace_count > 0 and not self._is_at_end():
            if self._check_symbol("{"):
                brace_count += 1
            elif self._check_symbol("}"):
                brace_count -= 1
        
            if brace_count > 0:  # Não avança no último }
                self._advance()
    
        end_token = self.current
        self._consume_symbol("}")
    
    # Cria e armazena a função
        function = QuokkaFunction(
            name=func_name,
            params=params,
            body=self.tokens[start_token:end_token],
            start_token=start_token,
            end_token=end_token
        )
    
        self.functions[func_name] = function
        print(f"Função '{func_name}' definida com {len(params)} parâmetros")

    def _execute_function_call(self, func_name: str, args: List[QuokkaValue]) -> QuokkaValue:
        """Executa uma chamada de função"""
        if func_name not in self.functions:
            raise QuokkaError(f"Função '{func_name}' não definida")
    
        function = self.functions[func_name]
    
    # Verifica número de argumentos
        if len(args) != len(function.params):
            raise QuokkaError(f"Função '{func_name}' espera {len(function.params)} argumentos, recebeu {len(args)}")
    
    # Cria novo ambiente para a função
        func_env = Environment(self.global_env)  # Funcões só veem globais + parâmetros

# Define parâmetros no ambiente da função
        for param_name, arg_value in zip(function.params, args):
            func_env.define(param_name, arg_value)

# Debug: mostra escopo da função
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"[DEBUG] Executando função '{func_name}' com escopo local")
            print(f"[DEBUG] Parâmetros: {dict(zip(function.params, args))}")
    
    # Salva estado atual
        old_env = self.current_env
        old_tokens = self.tokens
        old_current = self.current
    
        try:
    # Configura ambiente da função
            self.current_env = func_env
            self.tokens = function.body
            self.current = 0
    
    # Executa corpo da função com controle de escopo
            def execute_function():
                self._execute_function_body()
                return None
    
            result = self._execute_with_local_scope(
                execute_function, 
                f"função '{func_name}'"
            )
            return result
        
        except YieldException as yield_result:
        # Função executou yield - retorna o valor
            return yield_result.value
    
        finally:
        # Restaura estado anterior
            self.current_env = old_env
            self.tokens = old_tokens
            self.current = old_current

    def _execute_function_body(self):
        """Executa o corpo de uma função"""
        while not self._is_at_end():
            self._execute_statement()

    def _execute_yield(self):
        """Executa comando yield"""
        self._consume_keyword("yield")
        self._consume_symbol("(")
    
    # Avalia a expressão do yield
        value = self._parse_expression()
    
        self._consume_symbol(")")
    
    # Lança exceção especial para implementar o yield
        raise YieldException(value)

    def _parse_function_call(self, func_name: str) -> QuokkaValue:
        """Analisa chamada de função"""
        self._consume_symbol("(")
    
    # Coleta argumentos
        args = []
        if not self._check_symbol(")"): 
            while True:  
                arg = self._parse_expression()
                args.append(arg)
            
            
                if self._check_symbol(","):
                    self._advance()  
                    continue  
                elif self._check_symbol(")"):
                    break  
                else:
                    raise QuokkaError("Esperado ',' ou ')' em argumentos da função")
    
        self._consume_symbol(")")
    
    # Executa a função
        return self._execute_function_call(func_name, args)

    def _execute_each(self):
        """
        Executa iterador each
        Sintaxe: each($coleção : item) { instruções }
        """
        self._consume_keyword("each")
        self._consume_symbol("(")
        
        # Verifica se tem o $ antes da coleção
        if not self._check_ooperator("$"):
            raise QuokkaError("Esperado '$' antes da coleção em each")
        
        self._advance()  # consome $
        
        # Nome da variável que contém a coleção
        if not self._check_type("IDENTIFIER"):
            raise QuokkaError("Esperado nome da coleção após '$' em each")
        
        collection_name = self._advance().value
        
        # Dois pontos
        self._consume_ooperator(":")
        
        # Nome da variável de iteração
        if not self._check_type("IDENTIFIER"):
            raise QuokkaError("Esperado nome da variável de iteração em each")
        
        item_var_name = self._advance().value
        
        self._consume_symbol(")")
        self._consume_symbol("{")
        
        # Salva posição do início do bloco each
        each_start_token = self.current
        
        # Pula o corpo do each para encontrar o final
        brace_count = 1
        while brace_count > 0 and not self._is_at_end():
            if self._check_symbol("{"):
                brace_count += 1
            elif self._check_symbol("}"):
                brace_count -= 1
            
            if brace_count > 0:  # Não avança no último }
                self._advance()
        
        each_end_token = self.current
        self._consume_symbol("}")
        
        # Obtém a coleção
        collection = self.current_env.get(collection_name)

        # Verifica o tipo da coleção
        if isinstance(collection, QuokkaArray):
        # Comportamento normal para arrays
            self._execute_each_iteration(
                collection,
                item_var_name,
                each_start_token,
                each_end_token
            )
        elif isinstance(collection, QuokkaDict):
            # 🆕 Itera sobre os valores do dicionário
            keys_array = QuokkaDict(list(collection.items.keys()))
            self._execute_each_iteration(
                keys_array,
                item_var_name,
                each_start_token,
                each_end_token
            )
        elif isinstance(collection, str):
            # 🆕 Converte string em array de caracteres
            char_array = QuokkaArray([char for char in collection])
            self._execute_each_iteration(
                char_array,
                item_var_name,
                each_start_token,
                each_end_token
            )
        else:
            raise QuokkaError(f"'{collection_name}' não é um array ou string válido para iteração")
    
    def _execute_each_iteration(self, collection: QuokkaArray, item_var_name: str, start_token: int, end_token: int):
        """
    Executa a iteração do each para cada elemento da coleção
    """
        # Salva estado atual
        old_tokens = self.tokens
        old_current = self.current
    
    # Extrai o corpo do each
        each_body = self.tokens[start_token:end_token]
    
        try:
        # Para cada item na coleção
            for iteration_index, item in enumerate(collection.items):
                try:
                # Cria novo ambiente para a iteração (herda do ambiente atual)
                    iteration_env = self.current_env.create_local_scope()

                # Define a variável de iteração com o valor atual
                    iteration_env.define(item_var_name, item)

                # Adiciona variável especial com índice da iteração (opcional)
                    iteration_env.define("__index__", iteration_index)

                # Debug: mostra escopo da iteração
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        print(f"[DEBUG] Iteração {iteration_index}: {item_var_name} = {item}")
                
                # Salva ambiente atual
                    old_env = self.current_env
                
                    try:
                    # Configura ambiente da iteração
                        self.current_env = iteration_env
                        self.tokens = each_body
                        self.current = 0
                    
                    # Executa o corpo do each
                        while not self._is_at_end():
                            self._execute_statement()
                
                    finally:
                        # Restaura ambiente anterior
                        self.current_env = old_env
                    
                except BreakException:
                    # Break no each - sai do loop completamente
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        print(f"[DEBUG] Break executado no each, iteração {iteration_index}")
                    break  # Sai do for loop, terminando o each
                except ContinueException:
                # Continue no each - pula para próxima iteração
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        print(f"[DEBUG] Continue executado no each, iteração {iteration_index}")
                    continue  # Continua o for loop para próxima iteração
        
        except Exception as e:
            # Se houve erro na iteração, limpa o escopo
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] Erro na iteração: {e}")
            raise
        finally:
            # Restaura estado anterior
            self.tokens = old_tokens
            self.current = old_current


    
    def _parse_program(self):
        """Analisa a estrutura do programa Quokka"""
        while not self._is_at_end():
            if self._check_keyword("global"):
                self._parse_global_block()
            elif self._check_keyword("fun"):
                self._parse_function()
            elif self._check_keyword("main"):
                self._parse_main()
            else:
                self._advance()  # Pula tokens não reconhecidos
    
    def _parse_global_block(self):
        """Analisa o bloco global"""
        self._consume_keyword("global")
        self._consume_symbol("{")
        
        # Processa declarações de variáveis globais
        while not self._check_symbol("}") and not self._is_at_end():
            if self._check_type("IDENTIFIER"):
                var_name = self._advance().value
                
                if self._check_ooperator("="):
                    self._advance()  # consome '='
                    value = self._parse_expression()
                    self.global_env.define(var_name, value)
                else:
                    # Variável sem valor inicial (null)
                    self.global_env.define(var_name, None)
            else:
                self._advance()
        
        self._consume_symbol("}")
    
    def _parse_main(self):
        """Analisa e executa o bloco main"""
        self._consume_keyword("main")
        self._consume_symbol("{")
        
        # Executa o bloco main
        self._execute_block()
        
        self._consume_symbol("}")

    
    def _execute_block(self):
        """Executa um bloco de comandos"""
        while not self._check_symbol("}") and not self._is_at_end():
            self._execute_statement()
    
    def _execute_statement(self):
        """Executa uma declaração"""
        if self._check_keyword("print"):
            self._execute_print()
        elif self._check_keyword("if"):
            self._execute_if()
        elif self._check_keyword("while"):          
            self._execute_while()
        elif self._check_keyword("yield"):         
            self._execute_yield()
        elif self._check_keyword("each"):
            self._execute_each()
        elif self._check_keyword("break"):         
            self._execute_break()
        elif self._check_keyword("continue"): 
            self._execute_continue()     
        elif self._check_type("IDENTIFIER"):
            self._execute_assignment_or_function_call()
        else:
            self._advance() 
    
    def _execute_print(self):
        """Executa comando print"""
        self._consume_keyword("print")
        self._consume_symbol("(")
        
        value = self._parse_expression()
        print(self._quokka_to_string(value))
        
        self._consume_symbol(")")
    
    def _execute_break(self):
        """Executa comando break"""
        self._consume_keyword("break")
        # Lança exceção especial para sair do loop
        raise BreakException()

    def _execute_continue(self):
        """Executa comando continue"""
        self._consume_keyword("continue")
        # Lança exceção especial para pular para próxima iteração
        raise ContinueException()
    
    def _execute_assignment_or_function_call(self):
        """Executa atribuição de variável ou chamada de função"""
        var_name = self._advance().value
    
    # Verifica se é nome composto (função com pontos)
        while self._check_ooperator("."):
            self._advance()  # consome '.'
            if not self._check_type("IDENTIFIER"):
                raise QuokkaError("Esperado nome após '.' em função")
            var_name += "." + self._advance().value
    
    # Verifica o que vem depois
        if self._check_ooperator("="):
        # É atribuição: var = value ou var = funcao()
            self._advance()  # =
            value = self._parse_expression()
            self.current_env.set(var_name, value)
         
        elif self._check_doperator("+="):
            # Operador aritmético composto +=
            self._execute_compound_arithmetic(var_name, "+=")
    
        elif self._check_doperator("-="):
            # Operador aritmético composto -=
            self._execute_compound_arithmetic(var_name, "-=")
    
        elif self._check_doperator("<<"):
            # Operador de append <<
            self._execute_append_operator(var_name)
    
        elif self._check_doperator("++"):
            # Operador de incremento ++
            self._execute_increment_decrement(var_name, "++")
    
        elif self._check_doperator("--"):
            # Operador de decremento --
            self._execute_increment_decrement(var_name, "--")
    
        elif self._check_symbol("[") or self._check_symbol("{"):
        # Atribuição a elemento: var[index] = value ou var{'key'} = value
            obj = self.current_env.get(var_name)
        
            if self._check_symbol("["):
            # Array access: var[index] = value
                self._advance()  # [
                index = self._parse_expression()
                self._consume_symbol("]")
                self._consume_ooperator("=")
                value = self._parse_expression()
            
                if isinstance(obj, QuokkaArray):
                    if isinstance(index, int):
                        obj[index] = value
                    else:
                        raise QuokkaError("Índice de array deve ser um número")
                else:
                    raise QuokkaError(f"'{var_name}' não é um array")
        
            elif self._check_symbol("{"):
            # Dictionary access: var{'key'} = value
                self._advance()  # {
                key_expr = self._parse_expression()
        
                if isinstance(key_expr, str):
                    key = key_expr
                else:
                    key = str(key_expr)
                self._consume_symbol("}")
                self._consume_ooperator("=")
                value = self._parse_expression()
            
                if isinstance(obj, QuokkaDict):
                    obj[key] = value
                else:
                    raise QuokkaError(f"'{var_name}' não é um dicionário")
    
        elif self._check_symbol("("):
        # É chamada de função sem atribuição: minha_funcao()
            self._parse_function_call(var_name)
    
        else:
        # Apenas referência à variável (não faz nada)
            pass
    
    def _execute_compound_arithmetic(self, var_name: str, operator: str):
        """Executa operadores aritméticos compostos += e -="""
        self._advance()  # consome o operador
        
        try:
            # Obtém o valor atual da variável
            current_value = self.current_env.get(var_name)
            
            # Analisa o valor da expressão
            expression_value = self._parse_expression()
            
            # Verifica se os tipos são compatíveis para aritmética
            if not isinstance(current_value, (int, float)):
                raise QuokkaError(f"Operador {operator} requer um número à esquerda")
                
            if not isinstance(expression_value, (int, float)):
                raise QuokkaError(f"Operador {operator} requer um número à direita")
            
            # Executa a operação
            if operator == "+=":
                new_value = current_value + expression_value
            elif operator == "-=":
                new_value = current_value - expression_value
            
            # Atualiza a variável
            self.current_env.set(var_name, new_value)
            
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] {var_name} {operator} {expression_value}: {current_value} -> {new_value}")
                
        except Exception as e:
            raise QuokkaError(f"Erro ao executar {operator} em '{var_name}': {str(e)}")
            raise QuokkaError(f"Operador '{operator}' só funciona com números. '{var_name}' é {type(current_value).__name__}")
    
        if not isinstance(expression_value, (int, float)):
            raise QuokkaError(f"Operador '{operator}' só funciona com números. Expressão é {type(expression_value).__name__}")
    
    # Executa a operação
        if operator == "+=":
            new_value = current_value + expression_value
        elif operator == "-=":
            new_value = current_value - expression_value
        else:
            raise QuokkaError(f"Operador aritmético '{operator}' não reconhecido")
    
    # Atualiza a variável
        self.current_env.set(var_name, new_value)
    
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"[DEBUG] {var_name} {operator} {expression_value} = {new_value}")

    def _execute_increment_decrement(self, var_name: str, operator: str):
        """Executa operadores de incremento ++ e decremento --"""
        self._advance()  # consome o operador
        
        try:
            # Obtém o valor atual da variável
            current_value = self.current_env.get(var_name)
            
            # Verifica se o tipo é compatível para incremento/decremento
            if not isinstance(current_value, (int, float)):
                raise QuokkaError(f"Operador {operator} só pode ser usado com números")
            
            # Executa a operação
            if operator == "++":
                new_value = current_value + 1
            else:  # operator == "--"
                new_value = current_value - 1
            
            # Atualiza a variável
            self.current_env.set(var_name, new_value)
            
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] {var_name} {operator}: {current_value} -> {new_value}")
                
        except Exception as e:
            raise QuokkaError(f"Erro ao executar {operator} em '{var_name}': {str(e)}")
            raise QuokkaError(f"Operador '{operator}' só funciona com números. '{var_name}' é {type(current_value).__name__}")
    
    # Executa a operação
        if operator == "++":
            new_value = current_value + 1
        elif operator == "--":
            new_value = current_value - 1
        else:
            raise QuokkaError(f"Operador '{operator}' não reconhecido")
    
    # Atualiza a variável
        self.current_env.set(var_name, new_value)
    
        if hasattr(self, 'debug_mode') and self.debug_mode:
            print(f"[DEBUG] {var_name}{operator} = {new_value}")

    def _execute_append_operator(self, var_name: str):
        """Executa operador de append << para arrays e dicionários"""
        self._advance()  # consome <<
    
        # Obtém a coleção atual
        collection = self.current_env.get(var_name)
    
        # Verifica o tipo da coleção
        if isinstance(collection, QuokkaArray):
            self._execute_array_append(collection, var_name)
        elif isinstance(collection, QuokkaDict):
            self._execute_dict_append(collection, var_name)
        else:
            raise QuokkaError(f"Operador '<<' só funciona com arrays ou dicionários. '{var_name}' é {type(collection).__name__}")

    def _execute_array_append(self, array: QuokkaArray, var_name: str):
        """Executa append em array usando operador <<"""
        # Analisa o valor ou estrutura a ser adicionada
        value = self._parse_expression()
    
        if isinstance(value, QuokkaArray):
            # Se o valor é um array, adiciona todos os elementos
            for item in value.items:
                array.append(item)
        
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] {var_name} << {value} (múltiplos elementos)")
        else:
            # Adiciona valor único
            array.append(value)
        
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] {var_name} << {value}")

    def _execute_dict_append(self, dictionary: QuokkaDict, var_name: str):
        """Executa append em dicionário usando operador <<"""
        # Verifica se é uma única chave-valor ou múltiplas
        if self._check_symbol("("):
            # Sintaxe: dict << ('chave' = valor)
            self._advance()  # (
        
            if not self._check_type("KEY"):
                raise QuokkaError("Esperada chave (com aspas simples) após '<<' em dicionário")
        
            key = self._advance().value
            self._consume_ooperator("=")
            value = self._parse_expression()
            self._consume_symbol(")")
        
            # Adiciona/atualiza a chave
            dictionary[key] = value
        
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] {var_name} << ('{key}' = {value})")
    
        elif self._check_symbol("{"):
            # Sintaxe: dict << { 'chave1' = valor1 . 'chave2' = valor2 }
            dict_to_append = self._parse_dictionary()
        
            # Adiciona todas as chaves do dicionário
            for key, value in dict_to_append.items.items():
                dictionary[key] = value
        
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] {var_name} << {dict_to_append} (múltiplas chaves)")
    
        else:
            raise QuokkaError("Sintaxe inválida para append em dicionário. Use: dict << ('chave' = valor) ou dict << { 'chave' = valor }")

    
    def _execute_if(self):
        """Executa estrutura condicional if com suporte a else if"""
        self._consume_keyword("if")
        self._consume_symbol("(")
    
        condition = self._parse_expression()
    
        self._consume_symbol(")")
        self._consume_symbol("{")
    
        if self._is_truthy(condition):
            self._execute_block()
            self._consume_symbol("}")
        
        # Se a condição foi verdadeira, pula todos os else/else if
            self._skip_else_chain()
        else:
        # Pula o bloco if
            self._skip_block()
        
        # Processa else/else if
            self._handle_else_chain()

    def _handle_else_chain(self):
        """Processa cadeia de else/else if"""
        while self._check_keyword("else"):
            self._advance()  # consume 'else'
        
        # Verifica se é else if
            if self._check_keyword("if"):
            # É um else if - processa recursivamente
                self._execute_if()
                return  # A recursão vai lidar com o resto da cadeia
            else:
            # É um else simples
                self._consume_symbol("{")
                self._execute_block()
                self._consume_symbol("}")
                return  # Fim da cadeia
    def _skip_else_chain(self):
            """Pula toda a cadeia de else/else if quando uma condição já foi verdadeira"""
            while self._check_keyword("else"):
                self._advance()  # consume 'else'
        
                if self._check_keyword("if"):
            # else if - pula a condição e o bloco
                    self._advance()  # consume 'if'
                    self._consume_symbol("(")
                    self._skip_expression()  
                    self._consume_symbol(")")
                    self._consume_symbol("{")
                    self._skip_block()
                else:
            # else simples - pula o bloco
                    self._consume_symbol("{")
                    self._skip_block()
                    return  # Fim da cadeia
                
    def _execute_while(self):
        """
    Executa loop while
    Sintaxe: while(condição) { instruções }
    """
        self._consume_keyword("while")
        self._consume_symbol("(")
    
    # Salva a posição da condição para re-avaliar
        condition_start = self.current
    
    # Avalia a condição inicial
        condition = self._parse_expression()
    
        self._consume_symbol(")")
        self._consume_symbol("{")
    
    # Salva a posição do corpo do while
        body_start = self.current
    
    # Pula o corpo do while para encontrar o final
        brace_count = 1
        while brace_count > 0 and not self._is_at_end():
            if self._check_symbol("{"):
                brace_count += 1
            elif self._check_symbol("}"):
                brace_count -= 1
        
            if brace_count > 0:  # Não avança no último }
                self._advance()
    
        body_end = self.current
        self._consume_symbol("}")
    
    # Executa o loop while
        self._execute_while_loop(condition_start, body_start, body_end)

    def _execute_while_loop(self, condition_start: int, body_start: int, body_end: int):
        
        old_current = self.current

        loop_count = 0
        max_loops = 10000  # Proteção contra loop infinito

        try:
            while loop_count < max_loops:
                loop_count += 1
            
            # Re-avalia a condição
                self.current = condition_start
                condition = self._parse_expression()
            
            # Debug opcional
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    print(f"[DEBUG] While loop {loop_count}: condição = {condition}")
            
            # Se condição é falsa, sai do loop
                if not self._is_truthy(condition):
                    break
            
            # Executa o corpo do while com controle de break/continue
                try:
                    def execute_while_body():
                    # Extrai o corpo do while
                        while_body = self.tokens[body_start:body_end]
                
                    # Salva tokens atuais
                        old_tokens = self.tokens
                        old_current_inner = self.current
                
                        try:
                        # Configura para executar o corpo
                            self.tokens = while_body
                            self.current = 0
                    
                        # Executa cada instrução do corpo
                            while not self._is_at_end():
                                self._execute_statement()
                
                        finally:
                        # Restaura tokens originais
                            self.tokens = old_tokens
                            self.current = old_current_inner
            
                # Executa o corpo com escopo local
                    self._execute_with_local_scope(
                        execute_while_body, 
                        f"while loop iteração {loop_count}"
                    )
            
                except BreakException:
                # Break foi chamado - sai do loop
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        print(f"[DEBUG] Break executado na iteração {loop_count}")
                    break
            
                except ContinueException:
                # Continue foi chamado - pula para próxima iteração
                    if hasattr(self, 'debug_mode') and self.debug_mode:
                        print(f"[DEBUG] Continue executado na iteração {loop_count}")
                    continue

        except Exception as e:
            if hasattr(self, 'debug_mode') and self.debug_mode:
                print(f"[DEBUG] Erro no while loop na iteração {loop_count}: {e}")
            raise

        finally:
        # Sempre restaura posição original
            self.current = old_current

    # Proteção contra loop infinito
        if loop_count >= max_loops:
            raise QuokkaError(f"Loop while executou {max_loops} iterações. Possível loop infinito.")

    
    def _skip_expression(self):
        """Pula uma expressão sem avaliá-la"""
    # Implementação simples: pula tokens até encontrar ')' ou '}' no nível correto
        paren_count = 0
        brace_count = 0
    
        while not self._is_at_end():
            if self._check_symbol("("):
                paren_count += 1
            elif self._check_symbol(")"):
                if paren_count == 0:
                    break
                paren_count -= 1
            elif self._check_symbol("{"):
                brace_count += 1
            elif self._check_symbol("}"):
                if brace_count == 0:
                    break
                brace_count -= 1
        
            self._advance()
    
    def _parse_expression(self) -> QuokkaValue:
        """Analisa uma expressão e retorna seu valor"""
        return self._parse_logical_or()
    
    def _parse_logical_or(self) -> QuokkaValue:
        """Analisa operador lógico OR (||)"""
        expr = self._parse_logical_and()
        
        while self._check_doperator("||"):
            self._advance()
            right = self._parse_logical_and()
            expr = self._is_truthy(expr) or self._is_truthy(right)
        
        return expr
    
    def _parse_logical_and(self) -> QuokkaValue:
        """Analisa operador lógico AND (&&)"""
        expr = self._parse_equality()
        
        while self._check_doperator("&&"):
            self._advance()
            right = self._parse_equality()
            expr = self._is_truthy(expr) and self._is_truthy(right)
        
        return expr
    
    def _parse_equality(self) -> QuokkaValue:
        """Analisa operadores de igualdade (== e !=)"""
        expr = self._parse_1comparison()
        
        while self._check_doperator("==") or self._check_doperator("!="):
            doperator = self._advance().value
            right = self._parse_1comparison()
            
            if doperator == "==":
                expr = expr == right
            else:  
                expr = expr != right
        
        return expr
    
    def _parse_1comparison(self) -> QuokkaValue:
        """Analisa operadores de comparação (>, <)"""
        expr = self._parse_2comparison()

        while self._match_ooperators([">", "<"]):
            ooperator = self._previous().value
            right = self._parse_2comparison()
            
            if ooperator == ">":
                expr = expr > right
            else: 
                expr = expr < right
        
        return expr
    def _parse_2comparison(self) -> QuokkaValue:
        """Analisa operadores de comparação (>=, <=)"""
        expr = self._parse_addition()


        while self._match_doperators([">=", "<="]):
            doperator = self._previous().value
            right = self._parse_addition()
            
            if doperator == ">=":
                expr = expr >= right
            else:  
                expr = expr <= right
        
        return expr
    
    def _parse_addition(self) -> QuokkaValue:
        """Analisa operadores de adição e subtração"""
        expr = self._parse_multiplication()
        
        while self._match_ooperators(["+", "-"]):
            ooperator = self._previous().value
            right = self._parse_multiplication()
            
            if ooperator == "+":
                # Em Quokka, + pode ser soma numérica ou concatenação de strings
                if isinstance(expr, str) or isinstance(right, str):
                    expr = self._quokka_to_string(expr) + self._quokka_to_string(right)
                else:
                    expr = expr + right
            else:  
                expr = expr - right
        return expr
    
    def _parse_multiplication(self) -> QuokkaValue:
        """Analisa operadores de multiplicação e divisão"""
        expr = self._parse_exponentiation() 
        
        while self._match_ooperators(["*", "/", "%"]):
            ooperator = self._previous().value
            right = self._parse_exponentiation() 
            
            if ooperator == "*":
                expr = expr * right
            elif ooperator == "%":
                if not isinstance(expr, int) or not isinstance(right, int):
                    raise QuokkaError("Módulo só funciona com números inteiros")
                if right == 0:
                    raise QuokkaError("Divisão por zero no operador módulo")
                expr = expr % right
            else:  
                if right == 0:
                    raise QuokkaError("Divisão por zero")
                expr = expr / right
        
        return expr
    
    def _parse_exponentiation(self) -> QuokkaValue:
        """Analisa operador de potenciação (right-associative)"""
        expr = self._parse_primary()
    
        # ** é right-associative: 2**3**2 = 2**(3**2) = 512
        if self._check_doperator("**"):
            self._advance()
            # Recursivo para ser right-associative
            right = self._parse_exponentiation()
        
            if not isinstance(expr, (int, float)) or not isinstance(right, (int, float)):
                raise QuokkaError("Potenciação só funciona com números")
        
            expr = expr ** right
    
        return expr
    
    def _parse_data_structure(self) -> QuokkaValue:
        """Analisa arrays e dicionários Quokka"""
        self._consume_symbol("{")
        
        if self._check_symbol("}"):
            # Array/dicionário vazio
            self._advance()
            return QuokkaArray()
        
        # Verifica se é array ou dicionário olhando o primeiro elemento
        is_dict = False
        saved_position = self.current
        
        # Tenta detectar se é dicionário (tem aspas simples seguidas de =)
        if self._check_type("KEY"):
            self._advance()  # key
            if self._check_ooperator("="):
                is_dict = True
        
        # Volta para a posição original
        self.current = saved_position
        
        if is_dict:
            return self._parse_dictionary()
        else:
            return self._parse_array()
    
    def _parse_array(self) -> QuokkaArray:
        """Analisa um array Quokka: { item1 . item2 . item3 }"""
        array = QuokkaArray()
        
        while not self._check_symbol("}") and not self._is_at_end():
            # Analisa um elemento
            element = self._parse_expression()
            array.append(element)
            
            # Verifica se há mais elementos (separados por .)
            if self._check_ooperator("."):
                self._advance()  # consome '.'
            elif not self._check_symbol("}"):
                raise QuokkaError("Esperado '.' ou '}' em array")
        
        self._consume_symbol("}")
        return array
    
    def _parse_dictionary(self) -> QuokkaDict:
        """Analisa um dicionário Quokka: { 'key1' = value1 . 'key2' = value2 }"""
        dictionary = QuokkaDict()
        
        while not self._check_symbol("}") and not self._is_at_end():
            # Analisa uma chave
            if not self._check_type("KEY"):
                raise QuokkaError("Esperada chave (com aspas simples) em dicionário")
            
            key = self._advance().value
            
            self._consume_ooperator("=")
            
            # Analisa o valor
            value = self._parse_expression()
            dictionary[key] = value
            
            # Verifica se há mais pares (separados por .)
            if self._check_ooperator("."):
                self._advance()  # consome '.'
            elif not self._check_symbol("}"):
                raise QuokkaError("Esperado '.' ou '}' em dicionário")
        
        self._consume_symbol("}")
        return dictionary
    
    def _parse_access_expression(self, obj: QuokkaValue) -> QuokkaValue:
        """Analisa acesso a arrays/dicionários: obj[index] ou obj{'key'}"""
        if self._check_symbol("["):
            # Acesso a array: obj[index]
            self._advance()  # [
            index = self._parse_expression()
            self._consume_symbol("]")
            
            if isinstance(obj, QuokkaArray):
                if isinstance(index, int):
                    return obj[index]
                else:
                    raise QuokkaError("Índice de array deve ser um número")
            else:
                raise QuokkaError("Tentativa de acessar índice em não-array")
        
        elif self._check_symbol("{"):
            # Acesso a dicionário: obj{'key'}
            self._advance()  # {
            key_expr = self._parse_expression()
        
            # Converte para string se necessário
            if isinstance(key_expr, str):
                key = key_expr
            else:
                key = str(key_expr)
        
            self._consume_symbol("}")
            
            if isinstance(obj, QuokkaDict):
                return obj[key]
            else:
                raise QuokkaError("Tentativa de acessar chave em não-dicionário")
        
        return obj
    
    def _parse_primary(self) -> QuokkaValue:
        """Analisa valores primários (números, strings, variáveis, arrays, dicionários, funções, etc.)"""
        if self._check_type("INT"):
            return int(self._advance().value)
    
        if self._check_type("FLOAT"):
            return float(self._advance().value)
    
        if self._check_type("STRING"):
            return self._advance().value

        if self._check_type("KEY"):
            return self._advance().value
    
        if self._check_keyword("true"):
            self._advance()
            return True
    
        if self._check_keyword("false"):
            self._advance()
            return False
    
        if self._check_keyword("null"):
            self._advance()
            return None
        if self._check_keyword("prompt"):
            self._advance()
            return self._execute_prompt()
    # Suporte para estruturas de dados
        if self._check_symbol("{"):
            return self._parse_data_structure()
    
        if self._check_type("IDENTIFIER"):
            var_name = self._advance().value
        
        # Verificar se é função de conversão
            if var_name in ["to_int", "to_float", "to_bool", "to_str"] and self._check_symbol("("):
                return self._execute_conversion_function(var_name)
        
        # Verifica se é nome composto (função com pontos)
            while self._check_ooperator("."):
                self._advance()  # consome '.'
                if not self._check_type("IDENTIFIER"):
                    raise QuokkaError("Esperado nome após '.' em função")
                var_name += "." + self._advance().value
        
        # Verifica se é chamada de função
            if self._check_symbol("("):
            # É chamada de função
                return self._parse_function_call(var_name)
            else:
            # É variável
                obj = self.current_env.get(var_name)
            
            # Verifica se há acesso a array/dicionário
                while self._check_symbol("[") or self._check_symbol("{"):
                    obj = self._parse_access_expression(obj)
            
                return obj
    
        if self._check_symbol("("):
            self._advance()  # (
            expr = self._parse_expression()
            self._consume_symbol(")")
            return expr
    
        raise QuokkaError(f"Expressão inválida: {self._peek().value}")

    # Métodos auxiliares
    def _skip_block(self):
        """Pula um bloco de código sem executar"""
        brace_count = 1
        while brace_count > 0 and not self._is_at_end():
            if self._check_symbol("{"):
                brace_count += 1
            elif self._check_symbol("}"):
                brace_count -= 1
            self._advance()
    
    def _is_truthy(self, value: QuokkaValue) -> bool:
        """Determina se um valor é considerado verdadeiro"""
        if value is None or value is False:
            return False
        if value == 0 or value == "":
            return False
        return True
    
    def _quokka_to_string(self, value: QuokkaValue) -> str:
        """Converte um valor Quokka para string"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, QuokkaArray):
            return str(value)
        elif isinstance(value, QuokkaDict):
            return str(value)
        else:
            return str(value)

    def _execute_prompt(self) -> str:
        """
        Executa função prompt()
        Sintaxe: prompt("mensagem")
        Retorna: string com input do usuário
        """
    # prompt já foi consumido em _parse_primary()
        self._consume_symbol("(")
    
    # Analisa a mensagem (deve ser uma expressão que resulte em string)
        message_expr = self._parse_expression()
        message = self._quokka_to_string(message_expr)
    
        self._consume_symbol(")")
    
    # Pede input do usuário e retorna como string
        user_input = input(message)
        return user_input

    def _execute_conversion_function(self, func_name: str) -> QuokkaValue:
        """
        Executa funções de conversão: to_int(), to_float(), to_bool(), to_str
        """
    # Nome da função já foi consumido
        self._consume_symbol("(")
    
    # Pega o argumento
        arg = self._parse_expression()
    
        self._consume_symbol(")")
    
    # Converte baseado no tipo
        try:
            if func_name == "to_int":
                if isinstance(arg, str):
                    return int(arg)
                elif isinstance(arg, float):
                    return int(arg)
                elif isinstance(arg, int):
                    return arg
                else:
                    raise ValueError(f"Não é possível converter {type(arg)} para int")
                
            elif func_name == "to_float":
                if isinstance(arg, str):
                    return float(arg)
                elif isinstance(arg, int):
                    return float(arg)
                elif isinstance(arg, float):
                    return arg
                else:
                    raise ValueError(f"Não é possível converter {type(arg)} para float")

            elif func_name == "to_bool":
                if isinstance(arg, str):
                    arg_lower = arg.lower().strip()
                    if arg_lower in ["true", "yes", "sim", "s", "1", "verdadeiro","y"]:
                        return True
                    elif arg_lower in ["false", "no", "não", "n", "0", "falso"]:
                        return False
                    else:
                        raise ValueError(f"'{arg}' não é um valor booleano válido")
                elif isinstance(arg, bool):
                    return arg
                elif isinstance(arg, int):
                    return arg != 0
                elif isinstance(arg, float):
                    return arg != 0.0
                else:
                    raise ValueError(f"Não é possível converter {type(arg)} para bool")
                    
            elif func_name == "to_str":
                if isinstance(arg, str):
                    return arg
                elif isinstance(arg, int):
                    return str(arg)
                elif isinstance(arg, float):
                    return str(arg)
                else:
                    raise ValueError(f"Não é possível converter {type(arg)} para float")
                
        except ValueError as e:
            raise QuokkaError(f"Erro na conversão {func_name}: {e}")
    
    # Métodos de controle de tokens
    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
            return self.tokens[self.current - 1]
        else:
            # Retorna o último token se já estiver no fim
            return self.tokens[-1]

    def _peek(self) -> Token:
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        else:
            # Retorna o último token se já estiver no fim
            return self.tokens[-1]

    def _previous(self) -> Token:
        if self.current - 1 < len(self.tokens) and self.current - 1 >= 0:
            return self.tokens[self.current - 1]
        else:
            return self.tokens[0]
    
    def _is_at_end(self) -> bool:
        return self.current >= len(self.tokens)
    
    def _check_type(self, token_type: str) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _check_keyword(self, keyword: str) -> bool:
        return self._check_type("KEYWORD") and self._peek().value == keyword
    
    def _check_symbol(self, symbol: str) -> bool:
        return self._check_type("SYMBOL") and self._peek().value == symbol
    
    def _check_doperator(self, doperator: str) -> bool:
        return self._check_type("DOPERATOR") and self._peek().value == doperator
    def _check_ooperator(self, ooperator: str) -> bool:
        return self._check_type("OOPERATOR") and self._peek().value == ooperator
    
    def _match_symbols(self, symbols: List[str]) -> bool:
        for symbol in symbols:
            if self._check_symbol(symbol):
                self._advance()
                return True
        return False
    
    def _match_doperators(self, doperators: List[str]) -> bool:
        for doperator in doperators:
            if self._check_doperator(doperator):
                self._advance()
                return True
        return False
    def _match_ooperators(self, ooperators: List[str]) -> bool:
        for ooperator in ooperators:
            if self._check_ooperator(ooperator):
                self._advance()
                return True
        return False
    
    def _consume_keyword(self, keyword: str):
        if self._check_keyword(keyword):
            self._advance()
        else:
            raise QuokkaError(f"Esperado '{keyword}', encontrado '{self._peek().value}'")
    
    def _consume_symbol(self, symbol: str):
        if self._check_symbol(symbol):
            self._advance()
        else:
            raise QuokkaError(f"Esperado '{symbol}', encontrado '{self._peek().value}'")
    def _consume_ooperator(self, ooperator: str):
        if self._check_ooperator(ooperator):
            self._advance()
        else:
            raise QuokkaError(f"Esperado '{ooperator}', encontrado '{self._peek().value}'")

# Teste com each (iterador de arrays)
if __name__ == "__main__":
    # Exemplo com each
    test_code = '''
    global{
        numeros = { 10 . 20 . 30 . 40 . 50 }
        frutas = { "maçã" . "banana" . "laranja" . "uva" }
        pessoas = {
            { 'nome' = "João" . 'idade' = 25 }
            .
            { 'nome' = "Maria" . 'idade' = 30 }
            .
            { 'nome' = "Pedro" . 'idade' = 22 }
        }
        soma = 0
        contador = 0
    }
    
    main{
        print("=== ITERANDO SOBRE NÚMEROS ===")
        each($numeros : numero) {
            print("Número: " + numero)
            soma = soma + numero
        }
        print("Soma total: " + soma)
        
        print("")
        print("=== ITERANDO SOBRE FRUTAS ===")
        each($frutas : fruta) {
            contador = contador + 1
            print(contador + ": " + fruta)
        }
        
        print("")
        print("=== ITERANDO SOBRE PESSOAS ===")
        each($pessoas : pessoa) {
            nome = pessoa{'nome'}
            idade = pessoa{'idade'}
            print("Nome: " + nome + ", Idade: " + idade)
            
            if(idade >= 25) {
                print("  -> Pessoa com 25+ anos")
            }
        }
        
        print("")
        print("=== TESTANDO ESCOPO ===")
        print("Variável 'numero' fora do each:")
        # Esta linha deveria dar erro se 'numero' não existir
        # numero seria undefined aqui pois só existe dentro do each
        
        print("Contador final: " + contador)
        print("Soma final: " + soma)
    }
    '''
    
    interpreter = QuokkaInterpreter()
    print("=== EXECUTANDO CÓDIGO QUOKKA COM EACH ===")
    interpreter.interpret(test_code) 