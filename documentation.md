# Documentação Oficial da Linguagem Quokka V1.0 beta

--- 

## Índice

1. [Introdução](#introdução)
2. [Sintaxe Básica](#sintaxe-básica)
3. [Tipos de Dados](#tipos-de-dados)
4. [Estrutura do Programa](#estrutura-do-programa)
5. [Variáveis e Escopo](#variáveis-e-escopo)
6. [Operadores](#operadores)
7. [Estruturas de Controle](#estruturas-de-controle)
8. [Funções](#funções)
9. [Estruturas de Dados](#estruturas-de-dados)
10. [Sistema de Entrada de Dados](#sistema-de-entrada-de-dados)
11. [Comandos Especiais](#comandos-especiais)
12. [Tratamento de Erros](#tratamento-de-erros)
13. [Exemplos Práticos](#exemplos-práticos)
14. [Boas Práticas](#boas-práticas)
15. [Limitações Conhecidas](#limitações-conhecidas)

---

## Sintaxe Básica

### Comentários

comentários são linhas do código que são ignoradas pelo computador e geralmente servem para descrever a funcionalidade de um código

```quokka
# Este é um comentário de linha
print("Hello World")  # Comentário no final da linha
# A função acima escreve "Hello World"
```

### Convenções de Nomenclatura

- **Variáveis:** *placeholder de valor mutável - letra minúscula* - `minhaVariavel`, `contador`, `nome_usuario`
- **Funções:** `minhaFuncao`, `calcular.imc`, `processar_dados`
- **Constantes:** *variável com valor definido que não se altera durante o código - letra maiúscula* - `VALOR_MAXIMO`, `PI`

### Delimitadores

são os símbolos usados para *delimitar* pedaços do código e isolar certos dados ou parâmetros

- **Blocos:** `{` e `}`
- **Parâmetros:** `(` e `)`
- **Arrays:** `{` e `}` com separador `.`
- **Acesso a arrays:** `[` e `]`
- **Acesso a dicionários:** `{` e `}`

---

## Tipos de Dados

### Tipos Primitivos

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `int` | Números inteiros | `42`, `-17`, `0` |
| `float` | Números decimais | `3.14`, `-2.5`, `0.0` |
| `string` | Cadeias de caracteres | `"Hello"`, `"Quokka"` |
| `bool` | Valores lógicos | `true`, `false` |
| `null` | Valor nulo/vazio | `null` |

### Literais de String

```quokka
# Strings com aspas duplas
nome = "João Silva"
mensagem = "Bem-vindo ao Quokka!"

# Escape de caracteres
texto = "Linha 1\nLinha 2" # \n quebra linha
aspas = "Ele disse: \"Olá!\"" # \"Olá!\" será escrito "Olá" e não Olá 
```

### Conversão de Tipos

Quokka realiza conversão automática quando necessário:

```quokka
resultado = "Idade: " + 25        # String + int = "Idade: 25"
soma = 10 + 3.14                  # int + float = 13.14
condicao = 0                      # 0 é considerado false
```

---

## Estrutura do Programa

Um programa Quokka possui três seções principais:

### 1. Bloco Global

```quokka
global{ # Declaração de variáveis globais
    contador = 0 # variável de valor 0
    nome = null # variável sem valor definido
    configuracao = { 'debug' = true . 'versao' = "1.0" } # dicionário simples com duas chaves
}
```
As variáveis definidas no bloco global{} podem ser chamadas ao decorrer de todo o código

### 2. Definições de Função

```quokka
fun minhaFuncao(parametro1, parametro2){ 
    # Corpo da função
    resultado = parametro1 + parametro2
    yield(resultado)
}
```

### 3. Bloco Main

```quokka
main{ 
    # Código principal do programa. Todo o código que será executado deve estar contido em 'main'
    print("Iniciando programa...")
    minhaFuncao(10, 20)
}
```

### Programa Mínimo

```quokka
main{
    print("Hello, Quokka!")
}
```

---

## Variáveis e Escopo

### Declaração de Variáveis

```quokka
# No bloco global
global{
    variavel_global = "Visível em todo lugar"
    contador = 0
}

# Dentro de funções
fun exemplo(){
    variavel_local = "Só existe nesta função"
    variavel_global = "Modifica a global"
}
```

### Regras de Escopo

1. **Escopo Global:** Variáveis declaradas no bloco `global{}`
2. **Escopo Local:** Variáveis criadas dentro de funções
3. **Escopo de Bloco:** Variáveis em estruturas de controle herdam do escopo pai
4. **Precedência:** Local > Global

### Atribuição

```quokka
# Atribuição simples
idade = 25
nome = "Maria"

# Atribuição a elementos de estruturas
pessoas[0] = "João" # elemento 0 do array 'pessoas' é "João"
dados{'nome'} = "Pedro" # elemento 'nome' no dicionário 'dados' vale "Pedro"
```

---

## Operadores

### Operadores Aritméticos

| Operador | Descrição | Exemplo |
|----------|-----------|---------|
| `+` | Adição/Concatenação | `5 + 3`, `"A" + "B"` |
| `-` | Subtração | `10 - 4` |
| `*` | Multiplicação | `6 * 7` |
| `/` | Divisão | `15 / 3` |

### Operadores de Comparação

| Operador | Descrição | Exemplo |
|----------|-----------|---------|
| `==` | Igualdade | `a == b` |
| `!=` | Diferença | `x != y` |
| `>` | Maior que | `idade > 18` |
| `<` | Menor que | `nota < 7` |
| `>=` | Maior ou igual | `valor >= 100` |
| `<=` | Menor ou igual | `temperatura <= 0` |

### Operadores Lógicos

| Operador | Descrição | Exemplo |
|----------|-----------|---------|
| `&&` | E lógico | `idade >= 18 && idade <= 65` |
| `\|\|` | OU lógico | `dia == "sábado" \|\| dia == "domingo"` |

### Operador de Atribuição

| Operador | Descrição | Exemplo |
|----------|-----------|---------|
| `=` | Atribuição | `x = 10` |

### Precedência de Operadores

1. `()` - Parênteses
2. `*`, `/` - Multiplicação e divisão
3. `+`, `-` - Adição e subtração
4. `>`, `<`, `>=`, `<=` - Comparação
5. `==`, `!=` - Igualdade
6. `&&` - E lógico
7. `||` - OU lógico
8. `=` - Atribuição

---

## Estruturas de Controle

### Estruturas Condicionais

#### if simples

```quokka
if(idade >= 18){ # condição para executar instrução
    print("Maior de idade")
}
```

#### if-else

```quokka
if(nota >= 7){
    print("Aprovado")
}
else{ # intrução a ser realizada se a condição estabelecida não se aplicar
    print("Reprovado")
}
```

#### else if 

```quokka
if(nota >= 9){
    print("Excelente")
}
else if(nota >= 7){
    print("Bom")
} 
else if(nota >= 5){
    print("Regular")
}
else{
    print("Insuficiente")
}
```

### Estruturas de Repetição

#### while

```quokka
contador = 0
while(contador < 10){ # enquanto a condição for verdadeira, a intrução é executada
    print("Contador: " + contador)
    contador = contador + 1
}
```

#### each (iterador de arrays)

```quokka
numeros = { 10 . 20 . 30 . 40 }

each($numeros : numero){ # a variável 'numero' representa o elemento do array 'numeros' da vez
    print("Número: " + numero) # escreve "Número" mais o número representado por 'numero' na vez
}
```

### Controle de Fluxo

Quokka não possui `break` ou `continue` nativos. Use variáveis de controle:

```quokka
# Em vez de break
continuar = true
while(continuar == true){
    # ... código ...
    if(condicao_saida){
        continuar = false
    }
}
```

---

## Funções

### Definição de Função

```quokka
fun nomeDaFuncao(parametro1, parametro2){ # 'fun' declara função, seguido pelo seu nome e os parâmetros entre ()
    # Corpo da função
    resultado = parametro1 + parametro2
    yield(resultado)  # Retorna valor. O nome da função agora pode ser chamado como uma variável que contém o valor calculado pela função
}
```

### Funções com Nomes Compostos

```quokka
fun calcular.imc(peso, altura){
    imc = peso / (altura * altura)
    yield(imc)
}

fun processar.dados(){
    print("Processando...")
}
```


### Chamada de Função

```quokka
# Função sem retorno
processar.dados()

# Função com retorno
resultado = calcular.imc(70, 1.75)
print("IMC: " + resultado)

# Função retornando resultado diretamente
valor = somar(10, 20)
```

### Parâmetros e Argumentos

```quokka
fun exemploParametros(obrigatorio, opcional){
    if(opcional == null || opcional == 0){
        obrigatório = "valor padrão"
    }
    
    print("Obrigatório: " + obrigatorio)
    print("Opcional: " + opcional)
}

# Chamadas
exemploParametros("teste")           # opcional será null
exemploParametros("teste", "extra")  # ambos definidos
```

### Retorno de Valores

```quokka
fun semRetorno(){
    print("Esta função não retorna valor")
    # Implicitamente retorna null
}

fun comRetorno(x){
    resultado = x * 2
    yield(resultado)  # Retorno explícito do resultado
}
```
A função yield() deve ter como parâmetro a variável que será retornada como valor da função

### Escopo de Funções

- Funções têm acesso a variáveis globais
- Parâmetros são locais à função
- Variáveis criadas na função são locais

```quokka
global{
    global_var = "Global"
}

fun exemploEscopo(parametro){
    local_var = "Local"
    global_var = "Modificado"  # Altera a global
    
    print(parametro)    # Parâmetro
    print(local_var)    # Local
    print(global_var)   # Global modificada
}
```

---

## Estruturas de Dados

### Arrays (Listas)

#### Declaração e Inicialização

```quokka
# Array vazio
lista_vazia = { }

# Array com elementos
numeros = { 10 . 20 . 30 . 40 . 50 }
nomes = { "Ana" . "Bruno" . "Carlos" }
misto = { 1 . "texto" . true . null }
```

#### Acesso a Elementos

```quokka
primeiro = numeros[0]    # 10
segundo = numeros[1]     # 20
ultimo = numeros[4]      # 50

# Índice inválido retorna null
inexistente = numeros[10]  # null
```

#### Modificação de Elementos

```quokka
numeros[0] = 100         # Modifica primeiro elemento
numeros[5] = 60          # Adiciona novo elemento (expande array)
```

#### Iteração com each

```quokka
frutas = { "maçã" . "banana" . "laranja" }

each($frutas : fruta){
    print("Fruta: " + fruta)
}
```

### Dicionários (Mapas)

#### Declaração e Inicialização

```quokka
# Dicionário vazio
dict_vazio = { }

# Dicionário com pares chave-valor
pessoa = {
    'nome' = "João" . 
    'idade' = 30 .
    'cidade' = "São Paulo"
}

# ou
configuracao = {
    'debug' = true .
    'versao' = 1.5 .
    'autor' = "Desenvolvedor"
}
```

#### Acesso a Elementos

```quokka
nome = pessoa{'nome'}      # "João"
idade = pessoa{'idade'}    # 30

# Chave inexistente retorna null
telefone = pessoa{'telefone'}  # null
```

#### Modificação de Elementos

```quokka
pessoa{'nome'} = "Maria"          # Modifica valor existente
pessoa{'telefone'} = "123456789"  # Adiciona nova chave
```

#### Iteração (Limitada)

```quokka
# Quokka não possui iteração direta de dicionários
# Use arrays de chaves se necessário

chaves = { "nome" . "idade" . "cidade" }
each($chaves : chave){
    valor = pessoa{chave}
    print(chave + ": " + valor)
}
```

### Arrays de Dicionários

```quokka
pessoas = {
    { 'nome' = "Ana" . 'idade' = 25 } .
    { 'nome' = "Bruno" . 'idade' = 30 } .
    { 'nome' = "Carlos" . 'idade' = 35 }
}

each($pessoas : pessoa){
    print("Nome: " + pessoa{'nome'} + ", Idade: " + pessoa{'idade'})
}
```

---

## Sistema de Entrada de Dados

### Comando capture

O comando `capture[]` é usado para obter entrada do usuário:

```quokka
capture[variavel]: tipo {
    prompt("mensagem")
}
```

#### Tipos Suportados

- `string` - Texto
- `int` - Número inteiro
- `float` - Número decimal
- `bool` - Valor booleano

#### Exemplos Básicos

```quokka
# Captura string
capture[nome]: string {
    prompt("Digite seu nome:")
}

# Captura número inteiro
capture[idade]: int {
    prompt("Digite sua idade:")
}

# Captura número decimal
capture[altura]: float {
    prompt("Digite sua altura (em metros):")
}

# Captura booleano
capture[ativo]: bool {
    prompt("Usuário ativo? (true/false):")
}
```

#### Captura em Estruturas de Dados

```quokka
# Captura para array
numeros = { 0 . 0 . 0 }
capture[numeros[0]]: int {
    prompt("Primeiro número:")
}

# Captura para dicionário
pessoa = { 'nome' = "" . 'idade' = 0 }
capture[pessoa{'nome'}]: string {
    prompt("Nome da pessoa:")
}
```

#### Validação Automática

```quokka
# Se o usuário digitar um valor inválido para o tipo,
# o sistema mostra erro automaticamente

capture[numero]: int {
    prompt("Digite um número:")  # Se digitar "abc", mostra erro
}
```

---

## Comandos Especiais

### print

Exibe valores na saída:

```quokka
print("Mensagem simples")
print("Valor: " + variavel)
print(42)
print(array_ou_dicionario)
```

### yield

Retorna valor de uma função:

```quokka
fun calcular(x, y){
    resultado = x + y
    yield(resultado) 
}
```

### Comando prompt (apenas dentro de capture)

```quokka
capture[entrada]: string {
    prompt("Digite algo:")  # Só funciona dentro de capture. Ainda não existem outras aplicações de 'prompt()', pois é um traço vestigial de versões anteriores, por isso, talvez, seja **substituído por print() no futuro**
}
```

---

## Tratamento de Erros

### Tipos de Erro

1. **Erros de Sintaxe**
   ```
   ERRO: Esperado '}', encontrado 'print'
   ```

2. **Erros de Execução**
   ```
   ERRO: Variável 'x' não definida
   ERRO: Divisão por zero
   ```

3. **Erros de Tipo**
   ```
   ERRO: Não foi possível converter 'abc' para int
   ```

### Comportamento de Erros

- O programa para na primeira ocorrência de erro
- Mensagens de erro incluem descrição do problema
- Não há sistema de try/catch (ainda não implementado)

### Debugging

```quokka
# Use print para debug
print("Valor de x: " + x)
print("Chegou aqui!") # Quokka é procedual, portanto é executada linha a linha até encontrar um erro e parar 

# Verifique valores antes de usar
if(variavel != null){
    # Use a variável
}
```

---

## Exemplos Práticos

### Calculadora Simples

```quokka
global{
    num1 = 0
    num2 = 0
    operacao = ""
    resultado = 0
}

fun somar(a, b){
    yield(a + b)
}

fun dividir(a, b){
    if(b == 0){
        print("Erro: divisão por zero")
        yield(0)
    }
    yield(a / b)
}

main{
    print("=== Calculadora ===")
    
    capture[num1]: float {
        prompt("Primeiro número:")
    }
    
    capture[operacao]: string {
        prompt("Operação (+, -, *, /):")
    }
    
    capture[num2]: float {
        prompt("Segundo número:")
    }
    
    if(operacao == "+"){
        resultado = somar(num1, num2)
    }
    else{
        if(operacao == "/"){
            resultado = dividir(num1, num2)
        }
    }
    
    print("Resultado: " + resultado)
}
```

### Sistema de Cadastro

```quokka
global{
    pessoas = { }
    total = 0
}

fun adicionarPessoa(nome, idade){
    nova_pessoa = {
        'nome' = nome .
        'idade' = idade .
        'id' = total + 1
    }
    
    pessoas[total] = nova_pessoa
    total = total + 1
    
    print("Pessoa cadastrada com ID: " + nova_pessoa{'id'})
}

fun listarPessoas(){
    if(total == 0){
        print("Nenhuma pessoa cadastrada")
        yield(null)
    }
    
    print("=== Lista de Pessoas ===")
    contador = 0
    
    while(contador < total){
        pessoa = pessoas[contador]
        print("ID: " + pessoa{'id'} + " - " + pessoa{'nome'} + " (" + pessoa{'idade'} + " anos)")
        contador = contador + 1
    }
}

main{
    continuar = true
    
    while(continuar == true){
        print("\n1-Cadastrar | 2-Listar | 0-Sair")
        
        opcao = 0
        capture[opcao]: int {
            prompt("Opção:")
        }
        
        if(opcao == 1){
            nome = ""
            idade = 0
            
            capture[nome]: string {
                prompt("Nome:")
            }
            
            capture[idade]: int {
                prompt("Idade:")
            }
            
            adicionarPessoa(nome, idade)
        }
        else{
            if(opcao == 2){
                listarPessoas()
            }
            else{
                if(opcao == 0){
                    continuar = false
                }
            }
        }
    }
}
```

---

## Boas Práticas

### Nomenclatura

```quokka
# ✅ Bom
idade_usuario = 25
calcular.imc()
VALOR_MAXIMO = 100

# ❌ Evitar
x = 25
funcao1()
valor = 100
```

### Estrutura de Código

```quokka
# ✅ Organize blocos claramente
global{
    # Todas as variáveis globais aqui
}

# Todas as funções aqui
fun minhaFuncao(){
    # ...
}

main{
    # Lógica principal aqui
}
```
O escopo main ainda é global, como o do global{}, mas isso não impede o usuário de seguir as boas práticas de organização e declarar suas variáveis globais no bloco destinado a isso

### Validação de Entrada

```quokka
# ✅ Sempre valide entradas críticas
capture[idade]: int {
    prompt("Idade:")
}

if(idade < 0 || idade > 120){
    print("Idade inválida!")
    idade = 0
}
```

### Comentários

```quokka
# ✅ Comente código complexo
fun calcularDesconto(preco, percentual){
    # Aplica desconto e garante que não seja negativo
    desconto = preco * (percentual / 100)
    preco_final = preco - desconto
    
    if(preco_final < 0){
        preco_final = 0  # Preço mínimo é zero
    }
    
    yield(preco_final)
}
```

### Tratamento de Casos Extremos

```quokka
fun dividir(a, b){
    # ✅ Sempre trate divisão por zero
    if(b == 0){
        print("Erro: divisão por zero")
        yield(0)
    }
    yield(a / b)
}

fun acessarArray(array, indice){
    # ✅ Verifique bounds do array
    if(indice < 0){
        yield(null)
    }
    yield(array[indice])  # Quokka retorna null para índices inválidos
}
```

---

## Limitações Conhecidas

### Funcionalidades Não Implementadas

algumas funcionalidades ainda não foram implementadas. Porém, nenhuma apresenta criticidade significativa de prioridade, portanto o desenvolvimento seguirá focado em consertar e melhorar features já existentes.

1. **Comandos de controle de fluxo:**
   - `break` e `continue` ou equivalentes em loops
   - `yield` múltiplo em funções

2. **Estruturas avançadas:**
   - `switch/case` ou equivalentes
   - `for` ou equivalente tradicional
   - `do-while` ou equivalentes

3. **Tratamento de erros:**
   - `try/catch/finally` ou equivalentes
   - Lançamento customizado de exceções

4. **Funcionalidades de sistema:**
   - Manipulação de arquivos e comunicação externa
   - Operações de rede
   - Chamadas de sistema

5. **Recursos avançados:**
   - Classes e orientação a objetos
   - Módulos e imports
   - Bibliotecas externas

### Workarounds

```quokka
# Em vez de break, use variável de controle
continuar = true
while(continuar == true){
    if(condicao_saida){
        continuar = false
    }
}

# Em vez de for, use while
i = 0
while(i < 10){
    # corpo do loop
    i = i + 1
}

# Em vez de múltiplos returns
fun exemploReturn(valor){
    resultado = null
    
    if(valor > 0){
        resultado = "positivo"
    }
    else{
        resultado = "não positivo"
    }
    
    yield(resultado)  # Único return
}
```
