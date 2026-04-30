import random


class Cell():
    """Representa uma célula do labirinto com paredes e estado de visita.

    Cada célula contém coordenadas (x, y), quatro flags de parede
    (north, south, east, west) e um flag visited usado por algoritmos de
    geração e resolução.
    """

    def __init__(self, x: int, y: int) -> None:
        """Inicializa a célula nas coordenadas fornecidas.

        Args:
            x: Coordenada horizontal da célula.
            y: Coordenada vertical da célula.
        """
        self.x = x
        self.y = y
        self.north = True
        self.south = True
        self.east = True
        self.west = True
        self.visited = False


class MazeGenerator:
    """Constrói e resolve um labirinto retangular.

    Fornece validação de entradas, geração por DFS, introdução de ciclos
    (quando não perfeito) e resolução por DFS/BFS, além de utilitários de
    acesso à vizinhança e serialização do labirinto.
    """

    def __init__(
        self,
        width: int,
        height: int,
        output_file: str,
        perfect: bool,
        entry: tuple[int, int],
        exit: tuple[int, int],
        seed: int | None = None
    ) -> None:
        """Inicializa o gerador e valida os parâmetros de entrada.

        Cria a grade de células, define entrada e saída, e aplica semente
        ao gerador aleatório quando fornecida.

        Args:
            width: Largura do labirinto (nº colunas).
            height: Altura do labirinto (nº linhas).
            output_file: Caminho do arquivo de saída.
            perfect: Se True gera labirinto perfeito (sem ciclos).
            entry: Tupla (x, y) para a entrada.
            exit: Tupla (x, y) para a saída.
            seed: Semente opcional para random.
        """
        self.validate_inputs(
            width,
            height,
            output_file,
            perfect,
            seed,
            entry,
            exit
        )

        self.width = width
        self.height = height
        self.output_file = output_file
        self.perfect = perfect
        self.seed = seed

        self.maze: list[Cell] = [
            Cell(x, y)
            for y in range(self.height)
            for x in range(self.width)
        ]

        self.visited_cells: list[Cell] = []
        self.visited_cells_resolution: list[Cell] = []
        self.pattern_cells: list[Cell] = []

        self.entry = self.get_cell(entry[0], entry[1])
        self.exit = self.get_cell(exit[0], exit[1])

        if self.seed is not None:
            random.seed(self.seed)

    def validate_inputs(
        self,
        width: int,
        height: int,
        output_file: str,
        perfect: bool,
        seed: int | None,
        entry: tuple[int, int],
        exit: tuple[int, int]
    ) -> None:
        """Valida tipos e limites dos parâmetros de criação do labirinto.

        Lança ValueError em caso de parâmetros inválidos para proteger as
        operações subsequentes.
        """

        if not isinstance(width, int) or width <= 0:
            raise ValueError("width must be a positive integer")

        if not isinstance(height, int) or height <= 0:
            raise ValueError("height must be a positive integer")

        if not isinstance(output_file, str) or not output_file.strip():
            raise ValueError("output_file must be a valid string")

        if not isinstance(perfect, bool):
            raise ValueError("perfect must be True or False")

        if seed is not None and not isinstance(seed, int):
            raise ValueError("seed must be an integer or None")

        if (
            not isinstance(entry, tuple)
            or len(entry) != 2
            or not all(isinstance(i, int) for i in entry)
        ):
            raise ValueError("entry must be a tuple like (x, y)")

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("entry is outside maze boundaries")

        if exit is not None:
            if (
                not isinstance(exit, tuple)
                or len(exit) != 2
                or not all(isinstance(i, int) for i in exit)
            ):
                raise ValueError("exit must be a tuple like (x, y)")

            if not (0 <= exit[0] < width and 0 <= exit[1] < height):
                raise ValueError("exit is outside maze boundaries")

            if entry == exit:
                raise ValueError("entry and exit cannot be the same")

    def get_cell(self, x: int, y: int) -> Cell:
        """Retorna a célula localizada nas coordenadas (x, y).

        Args:
            x: Coordenada x desejada.
            y: Coordenada y desejada.

        Returns:
            A instância Cell correspondente.

        Raises:
            ValueError: Se não encontrar a célula nas coordenadas.
        """
        for cell in self.maze:
            if x == cell.x and y == cell.y:
                return cell
        raise ValueError(f"Cell with coordinates ({x}, {y})"
                         f" not found in the maze.")

    def pattern(self) -> None:
        """Aplica um padrão central de células visitadas no labirinto.

        Marca um conjunto predefinido de células como visitadas e as guarda
        em pattern_cells. Lança ValueError se a entrada ou saída estiverem
        no caminho do padrão.
        """
        x = self.width // 2
        y = self.height // 2

        coords = [
            # 4 format
            (y, x-1), (y, x-2), (y, x-3), (y-1, x-3), (y-2, x-3),
            (y+1, x-1), (y+2, x-1),

            # 2 format
            (y, x+1), (y, x+2), (y, x+3), (y-1, x+3),
            (y-2, x+3), (y-2, x+2),
            (y-2, x+1), (y+1, x+1), (y+2, x+1), (y+2, x+2),
            (y+2, x+3)
            ]
        for coord in coords:
            cell = self.get_cell(coord[1], coord[0])
            if cell == self.entry or cell == self.exit:
                raise ValueError("The pattern cannot be applied because"
                                 "the entry or exit is in the way.")
            cell.visited = True
            self.pattern_cells.append(cell)

    def get_neighboard(self, cell: Cell, neigboards: list[Cell]) -> None:
        """Preenche a lista com vizinhos não visitados da célula atual.

        Args:
            cell: Célula cujo entorno será verificado.
            neigboards: Lista a ser preenchida com células vizinhas.
        """
        if cell.x + 1 < self.width:
            cell_e = self.get_cell(cell.x + 1, cell.y)
            if not cell_e.visited:
                neigboards.append(cell_e)
        if cell.x - 1 >= 0 and cell.x - 1 < self.width:
            cell_w = self.get_cell(cell.x - 1, cell.y)
            if not cell_w.visited:
                neigboards.append(cell_w)
        if cell.y + 1 < self.height:
            cell_s = self.get_cell(cell.x, cell.y + 1)
            if not cell_s.visited:
                neigboards.append(cell_s)
        if cell.y - 1 >= 0 and cell.y - 1 < self.height:
            cell_n = self.get_cell(cell.x, cell.y - 1)
            if not cell_n.visited:
                neigboards.append(cell_n)

    def get_random_neighboard(self, neigboards: list[Cell]) -> Cell | None:
        """Retorna um vizinho aleatório dentre os não visitados.

        Args:
            neigboards: Lista de candidatos.

        Returns:
            Um Cell escolhido aleatoriamente ou None se a lista estiver vazia.
        """
        new_neighboard: list[Cell] = []
        for neighboard in neigboards:
            if not neighboard.visited:
                new_neighboard.append(neighboard)
        return random.choice(new_neighboard) if new_neighboard else None

    def remove_wall(self, cell: Cell, neighboard: Cell) -> None:
        """Remove a parede entre duas células adjacentes.

        Atualiza o estado das paredes das duas células conforme a posição
        relativa entre elas.
        """
        if cell.x > neighboard.x:
            cell.west = False
            neighboard.east = False
        elif cell.x < neighboard.x:
            cell.east = False
            neighboard.west = False
        elif cell.y > neighboard.y:
            cell.north = False
            neighboard.south = False
        elif cell.y < neighboard.y:
            cell.south = False
            neighboard.north = False

    def dfs(self, cell: Cell) -> None:
        """Gera caminhos recursivamente por busca em profundidade (DFS).

        Marca células como visitadas, remove paredes e recorre sobre os
        vizinhos até esgotar as opções.
        """
        cell.visited = True
        self.visited_cells.append(cell)
        while True:
            neighbors: list[Cell] = []
            self.get_neighboard(cell, neighbors)
            if not neighbors:
                return
            neighbor = random.choice(neighbors)
            # neighbor = self.get_random_neighboard(neighbors)
            if not neighbor:
                break
            self.remove_wall(cell, neighbor)
            neighbors.remove(neighbor)
            self.dfs(neighbor)
        return

    def reset_visited(self) -> None:
        """Restaura o estado 'visited' de todas as células para False."""
        for cell in self.maze:
            cell.visited = False

    def get_neighboard_opened(self,
                              cell: Cell,
                              neigboards: list[Cell]) -> None:
        """Preenche a lista com vizinhos acessíveis (paredes abertas).

        Args:
            cell: Célula atual.
            neigboards: Lista a ser preenchida com vizinhos abertos e
                não visitados.
        """
        if cell.x + 1 < self.width:
            cell_e = self.get_cell(cell.x + 1, cell.y)
            if not cell_e.visited and not cell.east and not cell_e.west:
                neigboards.append(cell_e)
        if cell.x - 1 >= 0 and cell.x - 1 < self.width:
            cell_w = self.get_cell(cell.x - 1, cell.y)
            if not cell_w.visited and not cell.west and not cell_w.east:
                neigboards.append(cell_w)
        if cell.y + 1 < self.height:
            cell_s = self.get_cell(cell.x, cell.y + 1)
            if not cell_s.visited and not cell_s.north and not cell.south:
                neigboards.append(cell_s)
        if cell.y - 1 >= 0 and cell.y - 1 < self.height:
            cell_n = self.get_cell(cell.x, cell.y - 1)
            if not cell_n.visited and not cell_n.south and not cell.north:
                neigboards.append(cell_n)

    def dfs_resolution(self, cell_entry: Cell, cell_exit: Cell) -> bool:
        """Resolve o labirinto por DFS recursiva e registra o caminho.

        Retorna True quando a saída é alcançada; caso contrário, False.
        """
        cell_entry.visited = True
        if cell_entry.x == cell_exit.x and cell_entry.y == cell_exit.y:
            return True
        self.visited_cells_resolution.append(cell_entry)
        neighbors: list[Cell] = []
        self.get_neighboard_opened(cell_entry, neighbors)
        if not neighbors:
            return False
        for neighbor in neighbors:
            if self.dfs_resolution(neighbor, cell_exit):
                return True
        self.visited_cells_resolution.pop()
        return False

    def bfs_resolution(self, cell_entry: Cell, cell_exit: Cell) -> None:
        """Resolve o labirinto por BFS e reconstrói o caminho encontrado.

        Executa busca em largura desde a entrada até a saída e preenche a
        lista visited_cells_resolution com o percurso final.
        """
        cell_entry.visited = True
        finish = Cell(-1, -1)
        queue = [cell_entry]
        parent = {cell_entry: finish}
        while queue:
            current = queue.pop(0)
            if current.x == cell_exit.x and current.y == cell_exit.y:
                break
            neighbors: list[Cell] = []
            self.get_neighboard_opened(current, neighbors)
            for neighbor in neighbors:
                if not neighbor.visited:
                    neighbor.visited = True
                    queue.append(neighbor)
                    parent[neighbor] = current
        current = cell_exit
        while current != finish:
            self.visited_cells_resolution.append(current)
            current = parent[current]
        self.visited_cells_resolution.reverse()

    def not_perfect_maze(self) -> None:
        """Introduce aberturas aleatórias para criar ciclos em labirintos.

        Percorre células e remove paredes de forma randômica evitando as
        células do padrão (pattern_cells).
        """
        for i in range(self.width * self.height):
            if i % 1 == 0:
                walls = ["north", "east", "south", "west"]
                cell = random.choice(self.maze)
                wall = random.choice(walls)
                if cell not in self.pattern_cells:
                    if wall == "north" and cell.north and not cell.y == 0:
                        neighbor = self.get_cell(cell.x, cell.y - 1)
                        if neighbor and neighbor not in self.pattern_cells:
                            cell.north = False
                            neighbor.south = False
                        if get_hex(cell) == "0" or get_hex(neighbor) == "0":
                            cell.north = True
                            if neighbor:
                                neighbor.south = True
                    elif wall == "east" and cell.east and not (
                                        cell.x == self.width - 1):
                        neighbor = self.get_cell(cell.x + 1, cell.y)
                        if neighbor and neighbor not in self.pattern_cells:
                            cell.east = False
                            neighbor.west = False
                        if get_hex(cell) == "0" or get_hex(neighbor) == "0":
                            cell.east = True
                            if neighbor:
                                neighbor.west = True
                    elif wall == "south" and cell.south and not (
                                        cell.y == self.height - 1):
                        neighbor = self.get_cell(cell.x, cell.y + 1)
                        if neighbor and neighbor not in self.pattern_cells:
                            cell.south = False
                            neighbor.north = False
                        if get_hex(cell) == "0" or get_hex(neighbor) == "0":
                            cell.south = True
                            if neighbor:
                                neighbor.north = True
                    elif wall == "west" and cell.west and not cell.x == 0:
                        neighbor = self.get_cell(cell.x - 1, cell.y)
                        if neighbor and neighbor not in self.pattern_cells:
                            cell.west = False
                            neighbor.east = False
                        if get_hex(cell) == "0" or get_hex(neighbor) == "0":
                            cell.west = True
                            if neighbor:
                                neighbor.east = True

    def generate(self) -> None:
        """Gera o labirinto e resolve o caminho entre entrada e saída.

        Executa padrão (quando aplicável), geração por DFS, introdução de
        ciclos quando não perfeito, reseta visitas e resolve por BFS.
        """
        if self.width > 8 or self.height > 8:
            self.pattern()
        self.dfs(self.maze[0])
        if not self.perfect:
            self.not_perfect_maze()
        self.reset_visited()
        self.bfs_resolution(self.entry, self.exit)


def get_hex(cell: Cell) -> str:
    """Retorna um dígito hexadecimal representando as paredes da célula.

    Bits: norte=1, leste=2, sul=4, oeste=8.
    """
    value = 0
    if cell.north:
        value |= 1
    if cell.east:
        value |= 2
    if cell.south:
        value |= 4
    if cell.west:
        value |= 8

    return format(value, "X")


def get_direction(cell1: Cell, cell2: Cell) -> str:
    """Determina a direção de cell1 para cell2 como 'N', 'S', 'E' ou 'W'.

    Retorna string vazia se as células forem iguais.
    """
    if cell1.x > cell2.x:
        return "W"
    elif cell1.x < cell2.x:
        return "E"
    elif cell1.y > cell2.y:
        return "N"
    elif cell1.y < cell2.y:
        return "S"
    return ""


def output_maze(maze: MazeGenerator) -> None:
    """Serializa o labirinto e a solução em um arquivo de saída.

    Escreve linhas hex por célula, seguido por entry/exit e a sequência
    de direções que descreve a solução.
    """
    line = ""
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.get_cell(x, y)
            line += get_hex(cell)
        line += "\n"
    line += "\n"
    line += f"{maze.entry.x}, {maze.entry.y}"
    line += "\n"
    line += f"{maze.exit.x}, {maze.exit.y}"
    line += "\n"
    visited_cells = maze.visited_cells_resolution
    for i in range(len(visited_cells) - 1):
        line += get_direction(visited_cells[i], visited_cells[i + 1])
    namefile = maze.output_file
    with open(namefile, "w") as f:
        f.write(line)
