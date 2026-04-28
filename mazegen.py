import random


class Cell():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.north = True
        self.south = True
        self.east = True
        self.west = True
        self.visited = False


class MazeGenerator:
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
        for cell in self.maze:
            if x == cell.x and y == cell.y:
                return cell
        raise ValueError(f"Cell with coordinates ({x}, {y})"
                         f" not found in the maze.")

    def pattern(self) -> None:
        x = self.width // 2
        y = self.height // 2

        coords = [
            # 4 format
            (y, x-1), (y, x-2), (y, x-3), (y-1, x-3), (y-2, x-3),
            (y+1, x-1), (y+2, x-1),

            # 2 format
            (y, x+1), (y, x+2), (y, x+3), (y-1, x+3),
            (y-2, x+3), (y-2, x+2),
            (y-2, x+1), (y+1, x+1), (y+2, x+1), (y+2, x+2), (y+2, x+3)
            ]
        for coord in coords:
            cell = self.get_cell(coord[1], coord[0])
            if cell == self.entry or cell == self.exit:
                raise ValueError("The pattern cannot be applied because"
                                 "the entry or exit is in the way.")
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

    def get_random_neighboard(self, neigboards: list[Cell]) -> Cell | None:
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
        for cell in self.maze:
            cell.visited = False

    def get_neighboard_opened(self,
                              cell: Cell,
                              neigboards: list[Cell]) -> None:

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
                    # ver se essa quebra de east e south ta funcionando
                    elif wall == "east" and cell.east and not (
                                        cell.x == self.width - 1):
                        cell.east = False
                        neighbor = self.get_cell(cell.x + 1, cell.y)
                        if neighbor and neighbor not in self.pattern_cells:
                            neighbor.west = False
                    elif wall == "south" and cell.south and not (
                                        cell.y == self.height - 1):
                        cell.south = False
                        neighbor = self.get_cell(cell.x, cell.y + 1)
                        if neighbor and neighbor not in self.pattern_cells:
                            neighbor.north = False
                    elif wall == "west" and cell.west and not cell.x == 0:
                        cell.west = False
                        neighbor = self.get_cell(cell.x - 1, cell.y)
                        if neighbor and neighbor not in self.pattern_cells:
                            neighbor.east = False

    def generate(self) -> None:
        if self.width > 8 or self.height > 8:
            self.pattern()
        self.dfs(self.maze[0])
        if not self.perfect:
            self.not_perfect_maze()
        self.reset_visited()
        self.bfs_resolution(self.entry, self.exit)


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
