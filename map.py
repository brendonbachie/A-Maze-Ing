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
        self.perfect = configuration.perfect
        self.maze = [Cell(x, y) for y in range(self.height) for x in range(self.width)]
        self.visited_cells = []
        self.visited_cells_resolution = []

    def get_cell(self, x, y) -> Cell:
        for cell in self.maze:
            if x == cell.x and y == cell.y:
                return cell
        return None

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
            neighbor = self.get_random_neighboard(neighbors)
            if not neighbor:
                break
            self.remove_wall(cell, neighbor)
            neighbors.remove(neighbor)
            self.dfs(neighbor)
        return

    def wall_neighboard_verify(self, cell: Cell, neighboard: Cell) -> bool:
        if cell.x > neighboard.x and cell.west and neighboard.east:
            return True
        if cell.x < neighboard.x and cell.east and neighboard.west:
            return True
        if cell.y > neighboard.y and cell.north and neighboard.south:
            return True
        if cell.y < neighboard.y and cell.south and neighboard.north:
            return True
        return False

    def get_neighboard_opened(self, cell: Cell, neigboards: list[Cell]) -> None:
        if cell.x + 1 < self.width:
            cell_e = self.get_cell(cell.x + 1, cell.y)
            if cell_e.visited and self.wall_neighboard_verify(cell, cell_e):
                neigboards.append(cell_e)
        if cell.x - 1 >= 0 and cell.x - 1 < self.width:
            cell_w = self.get_cell(cell.x - 1, cell.y)
            if cell_w.visited and self.wall_neighboard_verify(cell, cell_w):
                neigboards.append(cell_w)
        if cell.y + 1 < self.height:
            cell_s = self.get_cell(cell.x, cell.y + 1)
            if cell_s.visited and self.wall_neighboard_verify(cell, cell_s):
                neigboards.append(cell_s)
        if cell.y - 1 >= 0 and cell.y - 1 < self.height:
            cell_n = self.get_cell(cell.x, cell.y - 1)
            if cell_n.visited and self.wall_neighboard_verify(cell, cell_n):
                neigboards.append(cell_n)

    def dfs_resolution(self, cell_entry: Cell, cell_exit: Cell) -> None:
        cell_entry.visited = False
        self.visited_cells_resolution.append(cell_entry)
        while True:
            neighbors = []
            self.get_neighboard_opened(cell_entry, neighbors)

            if not neighbors:
                return

            neighbor = self.get_random_neighboard(neighbors)
            if not neighbor:
                break
            if cell_entry.x == cell_exit.x and cell_entry.y == cell_exit.y:
                break
            neighbors.remove(neighbor)
            self.dfs_resolution(neighbor)
        return