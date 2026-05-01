# MazeGen-Py

Gere labirintos retangulares em formato `.txt` com solução automática.

## Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/A-Maze-Ing.git
   cd A-Maze-Ing/mazegen-py
   ```

2. **Crie um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências e construa o pacote:**
   ```bash
   pip install --upgrade pip
   pip install .
   ```

## Build manual (opcional)

Para gerar o pacote `.whl`:
```bash
python3 -m build
```

## Como gerar um labirinto `.txt`

Crie um script Python, por exemplo `gerar_labirinto.py`:

```python
from mazegen import MazeGenerator

# Parâmetros: largura, altura, arquivo_saida, perfeito, entrada, saída, semente
maze = MazeGenerator(
    width=8,
    height=8,
    output_file="labirinto.txt",
    perfect=True,
    entry=(0, 0),
    exit=(7, 7),
    seed=42
)
maze.generate()
```

Execute:
```bash
python3 gerar_labirinto.py
```

O arquivo `labirinto.txt` será criado no diretório atual.

## Formato do arquivo `.txt`

- Cada linha representa uma linha do labirinto, cada célula é um dígito hexadecimal (paredes).
- Depois, as coordenadas de entrada e saída.
- Por fim, a sequência de direções da solução (`N`, `S`, `E`, `W`).

---

**Autores:** Brendon Bachie, Daniel Vieira
