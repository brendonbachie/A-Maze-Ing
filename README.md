# A-Maze-Ing

*This project has been created as part of the 42 curriculum by brendon-bachie, daniel-vieira.*

---

## Descrição

A-Maze-Ing é um gerador e visualizador de labirintos escrito em Python 3.10+. O programa lê um arquivo de configuração, gera um labirinto aleatório usando o algoritmo **Recursive Backtracker (DFS)**, resolve com **BFS** e exibe o resultado visualmente usando a biblioteca **MiniLibX (MLX)**.

O labirinto pode ser **perfeito** (exatamente um caminho entre quaisquer duas células) ou **imperfeito** (múltiplos caminhos). Todo labirinto contém um padrão **"42"** visível, formado por células totalmente fechadas no centro. O projeto inclui também um **modo jogo** inspirado na mitologia grega: Teseu persegue o Minotauro automaticamente, e ao alcançá-lo o jogador assume o controle para levar Teseu até a saída — com a opção de ativar o **Fio de Ariadne** como guia.

A lógica de geração também está disponível como um **pacote pip standalone** (`mazegen`) reutilizável em projetos futuros.

---

## Instruções

### Requisitos

- Python 3.10 ou superior
- MiniLibX (MLX) — incluída no projeto
- `pip install build` para buildar o pacote mazegen

### Instalação

```bash
make install
```

### Executar

```bash
make run
# ou diretamente:
python3 a_maze_ing.py config.txt
```

### Modo debug

```bash
make debug
```

### Lint

```bash
make lint
```

### Limpar arquivos temporários

```bash
make clean
```

---

## Formato do Arquivo de Configuração

O programa lê um arquivo de texto simples com um par `CHAVE=VALOR` por linha. Linhas começando com `#` são comentários e são ignoradas.

### Chaves obrigatórias

| Chave         | Descrição                                | Exemplo                  |
|---------------|------------------------------------------|--------------------------|
| `WIDTH`       | Largura do labirinto em células          | `WIDTH=20`               |
| `HEIGHT`      | Altura do labirinto em células           | `HEIGHT=15`              |
| `ENTRY`       | Coordenadas de entrada (x,y)             | `ENTRY=0,0`              |
| `EXIT`        | Coordenadas de saída (x,y)               | `EXIT=19,14`             |
| `OUTPUT_FILE` | Nome do arquivo de saída (deve ser .txt) | `OUTPUT_FILE=maze.txt`   |
| `PERFECT`     | Labirinto perfeito? (`True` ou `False`)  | `PERFECT=True`           |

### Chaves opcionais

| Chave      | Descrição                                               | Exemplo           |
|------------|---------------------------------------------------------|-------------------|
| `SEED`     | Semente inteira para geração reproduzível               | `SEED=42`         |
| `GAMEMODE` | Habilita o modo jogo (`True` ou `False`)                | `GAMEMODE=True`   |
| `TESEU`    | Posição inicial de Teseu (x,y) — exige GAMEMODE=True    | `TESEU=0,0`       |
| `MINOTAUR` | Posição inicial do Minotauro (x,y) — exige GAMEMODE=True | `MINOTAUR=10,7` |

### Exemplo de configuração padrão

```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
GAMEMODE=True
TESEU=0,0
MINOTAUR=10,7
```

---

## Controles

### Modo normal

| Tecla   | Ação                                      |
|---------|-------------------------------------------|
| `G`     | Gerar o labirinto (animado)               |
| `S`     | Resolver o labirinto (animado)            |
| `R`     | Resetar e gerar um novo labirinto         |
| `C`     | Mudar as cores aleatoriamente             |
| `P`     | Mostrar/esconder o caminho de solução     |
| `SPACE` | Pular a animação atual                    |
| `M`     | Abrir o modo jogo (requer GAMEMODE=True)  |
| `ESC`   | Sair                                      |

### Modo jogo

| Tecla   | Ação                                                  |
|---------|-------------------------------------------------------|
| `S`     | Iniciar a perseguição automática Teseu/Minotauro      |
| `Setas` | Mover Teseu (após capturar o Minotauro)               |
| `A`     | Ativar/desativar o Fio de Ariadne (caminho dourado)   |
| `ESC`   | Sair                                                  |

---

## Algoritmo de Geração

O projeto usa o algoritmo **Recursive Backtracker (DFS)**, também conhecido como busca em profundidade aleatória.

### Por que DFS?

Produz labirintos com corredores longos e tortuosos — esteticamente interessantes e com aparência de labirinto clássico. Garante conectividade total: toda célula é acessível a partir de qualquer outra (propriedade de labirinto perfeito). A implementação recursiva é simples e mapeia diretamente para teoria de grafos: o resultado é uma **árvore geradora** do grafo completo da grade. A reproduzibilidade é controlada facilmente via `random.seed()`.

### Como funciona

1. Começa na célula (0,0) e a marca como visitada.
2. Coleta todos os vizinhos não visitados.
3. Escolhe um aleatoriamente com `random.choice()`.
4. Remove a parede entre a célula atual e o vizinho escolhido.
5. Chama recursivamente o DFS no vizinho.
6. Quando não há mais vizinhos (beco sem saída), faz backtrack.

Para labirintos imperfeitos (`PERFECT=False`), paredes adicionais são removidas aleatoriamente após a geração para criar múltiplos caminhos.

### Resolução

O labirinto é resolvido com **BFS (Busca em Largura)**, que garante o caminho mais curto entre entrada e saída em um grafo não ponderado.

---

## Formato do Arquivo de Saída

O labirinto é escrito linha por linha, um dígito hexadecimal por célula. Cada dígito codifica as paredes fechadas como bitmask:

| Bit     | Direção |
|---------|---------|
| 0 (LSB) | Norte   |
| 1       | Leste   |
| 2       | Sul     |
| 3       | Oeste   |

Parede fechada = bit 1, aberta = bit 0.

Após uma linha vazia, o arquivo contém:
1. Coordenadas de entrada: `x, y`
2. Coordenadas de saída: `x, y`
3. Caminho mais curto da entrada à saída usando as letras `N`, `E`, `S`, `W`

---

## Módulo Reutilizável (mazegen)

A lógica de geração está disponível como pacote pip standalone chamado `mazegen`, localizado na raiz deste repositório. O pacote não tem dependências externas — só a biblioteca padrão do Python.

### O que inclui

- `Cell` — representa uma célula do labirinto com estados de parede (norte, sul, leste, oeste).
- `MazeGenerator` — gera e resolve labirintos recebendo parâmetros puros, sem depender de nenhum outro arquivo do projeto.
- `get_hex`, `get_direction`, `output_maze` — utilitários de output.

### Como buildar

```bash
pip install build
python -m build
# Saída: dist/mazegen-1.0.0-py3-none-any.whl
```

### Como instalar

```bash
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

### Exemplo básico de uso

```python
from mazegen import MazeGenerator, output_maze

mg = MazeGenerator(
    width=20,
    height=15,
    output_file="maze.txt",
    perfect=True,
    entry=(0, 0),
    exit=(19, 14),
    seed=42
)

mg.generate()  # gera e resolve o labirinto

# Acessar a estrutura do labirinto
for cell in mg.maze:
    print(cell.x, cell.y, cell.north, cell.east, cell.south, cell.west)

# Acessar o caminho da solução
for cell in mg.visited_cells_resolution:
    print(cell.x, cell.y)

# Salvar arquivo de saída
output_maze(mg)
```

### Parâmetros personalizados

```python
# Sem seed (aleatório a cada execução)
mg = MazeGenerator(width=30, height=30, output_file="saida.txt",
                   perfect=False, entry=(0, 0), exit=(29, 29))

# Com seed (reproduzível)
mg = MazeGenerator(width=10, height=10, output_file="saida.txt",
                   perfect=True, entry=(0, 0), exit=(9, 9), seed=123)
```

---

## Equipe e Gestão do Projeto

### Papéis

- **Daniel Vieira** — algoritmo de geração (DFS/BFS), formato do arquivo de saída, validate_config, lógica do jogo.
- **Brendon Bachie** — arquitetura e refatoração do projeto, visualização MLX, funções de desenho, animações, gráficos do modo jogo, key hooks, Fio de Ariadne.

### Planejamento e evolução

O planejamento inicial focou na parte obrigatória: leitura de configuração, geração do labirinto, arquivo de saída e exibição básica com MLX. O modo jogo e o pacote mazegen foram desenvolvidos em uma segunda fase. O código foi progressivamente refatorado de um único `main.py` para arquivos separados (`state.py`, `draw.py`, `hooks.py`, `a_maze_ing.py`) para melhorar a legibilidade e a separação de responsabilidades.

O que funcionou bem: a combinação DFS/BFS se mostrou sólida e produziu labirintos corretos de forma consistente. O sistema de hooks do MLX (key, expose, loop) foi direto uma vez compreendido.

O que poderia melhorar: o modo jogo passou por várias iterações de design — a perseguição automática inicial entre Teseu e Minotauro foi difícil de equilibrar, levando à abordagem híbrida (fase automática + fase controlada pelo jogador) usada na versão final.

### Ferramentas utilizadas

- Python 3.10+
- MiniLibX (MLX) — exibição gráfica
- mypy — verificação estática de tipos
- flake8 — linting
- setuptools / build — geração do pacote pip

---

## Uso de IA

O Claude (Anthropic) foi utilizado ao longo do projeto como assistente de desenvolvimento. Os principais usos foram: depuração de problemas de renderização MLX (ordenação do expose hook, distinção entre desenho na imagem e na janela diretamente), discussão de decisões de arquitetura (separação de arquivos, design do modo jogo), explicação do comportamento dos algoritmos (reconstrução de caminho no BFS, backtracking no DFS) e revisão de código. Todo conteúdo gerado pela IA foi compreendido, testado e adaptado pela equipe antes de ser incluído no projeto.

## Recursos

Foi utilizado o guia feito pelos cadetes Lunna e Thalles. Foi utilizado tutorial para o DFS e BFS (https://medium.com/@anwarhermuche/m%C3%A9todos-de-busca-em-grafos-bfs-dfs-cf17761a0dd9) e Os recursos de IA Claude e ChatGPT para auxílio de entendimento dos algoritmos e da refatoração.

### Módulo Reutilizável:

Dentro do módulo `mazegen`, a classe `MazeGenerator` é a peça central. Ela encapsula toda a lógica de geração e resolução do labirinto, permitindo que seja facilmente reutilizada em outros projetos sem dependências externas. A classe é projetada para ser flexível, aceitando parâmetros de configuração diretamente no construtor, o que facilita a criação de labirintos personalizados.

Exemplo de uso do `MazeGenerator`:

```python
import mazegen

mg = mazegen.MazeGenerator(
    width=20,
    height=15,
    output_file="maze.txt",
    perfect=True,
    entry=(0, 0),
    exit=(19, 14),
    seed=42
)
mg.generate()  # Gera e resolve o labirinto
