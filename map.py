import validate_config
import random


class Cell():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.north = True
        self.south = True
        self.east = True
        self.west = True
        self.visited = False



class MazeGenerator():
    def __init__(self, configuration: validate_config.Configuration):
        self.width = configuration.width
        self.height = configuration.height
        self.entry = configuration.entry
        self.exit = configuration.exit
        self.output_file = configuration.output_file
        self.perfect = configuration.perfect
        self.seed = configuration.seed
        self.maze = [Cell(x, y) for y in range(self.height) for x in range(self.width)]
        self.visited_cells = []
        self.visited_cells_resolution = []
        self.pattern_cells = []

        if self.seed is not None:
            random.seed(self.seed)

    def get_cell(self, x, y) -> Cell:
        for cell in self.maze:
            if x == cell.x and y == cell.y:
                return cell
        return None

    def pattern(self) -> list[Cell]:
        x = self.width // 2
        y = self.height // 2

        coords = [
            # 4 format
            (y, x-1), (y, x-2), (y, x-3), (y-1, x-3), (y-2, x-3),
            (y+1, x-1), (y+2, x-1),

            # 2 format
            (y, x+1), (y, x+2), (y, x+3), (y-1, x+3), (y-2, x+3), (y-2, x+2),
            (y-2, x+1), (y+1, x+1), (y+2, x+1), (y+2, x+2), (y+2, x+3)
            ]
        for coord in coords:
            cell = self.get_cell(coord[1], coord[0])
            cell.visited = True
            self.pattern_cells.append(cell)

    def get_neighboard(self, cell: Cell, neigboards: list[Cell]) -> None:
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

    def get_random_neighboard(self, neigboards: list[Cell]) -> Cell:
        new_neighboard: list[Cell] = []
        for neighboard in neigboards:
            if not neighboard.visited:
                new_neighboard.append(neighboard)
        return random.choice(new_neighboard) if new_neighboard else None

    def remove_wall(self, cell: Cell, neighboard: Cell) -> None:
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
        cell.visited = True
        self.visited_cells.append(cell)
        while True:
            neighbors = []
            self.get_neighboard(cell, neighbors)

            if not neighbors:
                return

            neighbor = random.choice(neighbors)
            #neighbor = self.get_random_neighboard(neighbors)
            if not neighbor:
                break
            self.remove_wall(cell, neighbor)
            neighbors.remove(neighbor)
            self.dfs(neighbor)
        return

    def reset_visited(self) -> None:
        for cell in self.maze:
            cell.visited = False

    def get_neighboard_opened(self, cell: Cell, neigboards: list[Cell]) -> None:
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
        cell_entry.visited = True
        if cell_entry.x == cell_exit.x and cell_entry.y == cell_exit.y:
            return True
        self.visited_cells_resolution.append(cell_entry)
        neighbors = []
        self.get_neighboard_opened(cell_entry, neighbors)
        if not neighbors:
            return False
        for neighbor in neighbors:
            if self.dfs_resolution(neighbor, cell_exit):
                return True
        self.visited_cells_resolution.pop()
        return False

    def bfs_resolution(self, cell_entry: Cell, cell_exit: Cell) -> None:
        cell_entry.visited = True
        queue = [cell_entry]
        parent = {cell_entry: None}
        while queue:
            current = queue.pop(0)
            if current.x == cell_exit.x and current.y == cell_exit.y:
                break
            neighbors = []
            self.get_neighboard_opened(current, neighbors)
            for neighbor in neighbors:
                if not neighbor.visited:
                    neighbor.visited = True
                    queue.append(neighbor)
                    parent[neighbor] = current
        current = cell_exit
        while current is not None:
            self.visited_cells_resolution.append(current)
            current = parent[current]
        self.visited_cells_resolution.reverse()

    def not_perfect_maze(self) -> None:
        for i in range(self.width * self.height):
            if i % 5 == 0:
                walls = ["north", "east", "south", "west"]
                cell = random.choice(self.maze)
                wall = random.choice(walls)
                if cell not in self.pattern_cells:
                    if wall == "north" and cell.north and not cell.y == 0:
                        cell.north = False
                        neighbor = self.get_cell(cell.x, cell.y - 1)
                        if neighbor and neighbor not in self.pattern_cells:
                            neighbor.south = False
                    elif wall == "east" and cell.east and not cell.x == self.width - 1:
                        cell.east = False
                        neighbor = self.get_cell(cell.x + 1, cell.y)
                        if neighbor and neighbor not in self.pattern_cells:
                            neighbor.west = False
                    elif wall == "south" and cell.south and not cell.y == self.height - 1:
                        cell.south = False
                        neighbor = self.get_cell(cell.x, cell.y + 1)
                        if neighbor and neighbor not in self.pattern_cells:
                            neighbor.north = False
                    elif wall == "west" and cell.west and not cell.x == 0:
                        cell.west = False
                        neighbor = self.get_cell(cell.x - 1, cell.y)
                        if neighbor and neighbor not in self.pattern_cells:
                            neighbor.east = False

def get_hex(cell: Cell) -> str:
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
    line = ""
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.get_cell(x, y)
            line += get_hex(cell)
        line += "\n"
    line += "\n"
    line += (f"{maze.entry[0]},{maze.entry[1]}\n{maze.exit[0]},{maze.exit[1]}\n")
    visited_cells = maze.visited_cells_resolution
    for i in range(len(visited_cells) - 1):
        line += get_direction(visited_cells[i], visited_cells[i + 1])
    namefile = maze.output_file
    with open(namefile, "w") as f:
        f.write(line)


'''Aqui vai ficar a questão do jogo, o teseu e o minotauro, a mudança de labirinto e as regras 

A principio, Teseu tera 20 movimentos no labirinto e minotauro 10. Pela mitologia original, 
Teseu matou o minotauro e saiu do labirinto. Então temos basicamente:
- Teseu tem 20 movimentos
- Minotauro tem 10 movimentos
- Se Teseu não chegar no Minotauro em 20 movimentos, algumas paredes do labirinto se movem, mudando o layout
- Se Teseu chegar no Minotauro, ele mata Minotauro, e aí pode sair do labirinto

Então precisamos de:

- Uma função para mover o Minotauro, aleatoriamente
- Uma função para mover o Teseu até o Minotauro, temos o bfs pra isso pronto
- Uma função para verificar se Teseu chegou no Minotauro
- Uma função para verificar se Teseu saiu do labirinto
- Uma função para mudar o layout do labirinto, movendo algumas paredes (talvez. Mudar paredes aparentemente é complicado, 
então talvez a gente só mude o layout do labirinto, gerando um novo labirinto, e colocando Teseu e Minotauro em posições aleatórias)'''

'''Vamos criar uma classe GameState para manter o estado do jogo, incluindo as posições de Teseu e Minotauro, o número de movimentos restantes, e o layout atual do labirinto.

Sempre que o contador de movimentos de teseu e minotauro chegar a 0, o layout do labirinto muda, mas os personagens ficam no mesmo lugar. O layout do labirinto muda gerando um novo labirinto, 
mas colocando Teseu e Minotauro no mesmo lugar, ou seja, se Teseu estava em (x, y), ele continua em (x, y) no novo labirinto, e o mesmo para o Minotauro. Então:

- Quando chamarmos a função de mudança de layout, ela gera um novo labirinto, mas coloca Teseu e Minotauro nas mesmas posições que eles estavam antes da mudança.
- Vamos alterar maze.entry e maze.exit para serem as posições de Teseu e Minotauro, respectivamente, para facilitar a resolução do labirinto usando o bfs.
- A função de mudança de layout pode ser chamada tanto quando o contador de movimentos de Teseu chega a 0, quanto quando o contador de movimentos do Minotauro chega a 0.
- A função de mudança de layout pode ser chamada também quando Teseu e Minotauro estão na mesma posição, ou seja, quando Teseu chega no Minotauro, ele mata o Minotauro, e aí pode sair do labirinto, 
então, temos que mudar o labirinto, e abrindo uma saída pra Teseu. Pode ter uma celula aleatória pintada no mapa como a saída, e aí podemos forçar uma mudança de layout se Minotauro passar pela saída, 
pra que ele sempre fique preso
- Temos que fazer uma função para Minotauro andar aleatoriamente, e uma função para Teseu andar até o Minotauro usando o bfs. O bfs pode ser chamado a cada movimento de Teseu, pra ele sempre andar na direção
do Minotauro, e o Minotauro pode andar aleatoriamente pelo labirinto. Dá pra pegar a posição de Minotauro, verificar celulas vizinhas sem parede, escolher uma aleatória e seguir, e diminuir o contador
de movimentos do Minotauro. O mesmo para Teseu, mas usando o bfs pra escolher a direção. A cada movimento, temos que verificar se Teseu chegou no Minotauro, ou se Teseu saiu do labirinto, ou se
Minotauro saiu do labirinto, e aí chamar a função de mudança de layout, ou terminar o jogo, dependendo do caso.

Tenho que mudar a MiniLibX também, pra desenhar apenas uma celula a cada frame, ao invés de desenhar o caminho percorrido todo, pra dar a impressão de que os personagens estão andando pelo labirinto, e 
não teletransportando, e aí a cada movimento, chamar a função de desenho, pra desenhar a nova posição dos personagens.'''