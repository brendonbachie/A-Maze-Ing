import mlx
import time
import random
import validate_config
from validate_config import Configuration as cfg
import map
from map import Cell
from enum import Enum
import sys
import game


class State(Enum):
    GENERATE = 1
    RESOLUTION = 2
    DONE = 3
    RESOLUTION_HIDDEN = 4
    RESOLUTION_SHOWN = 5
    NOT_RESOLUTION = 6
    TESEU = 7
    MINOTAUR = 8
    GAME = 9
    PLAYER_MOVE = 10


class MazeState():
    def __init__(self) -> None:
        self.config: cfg = validate_config.read_config_file()
        self.maze: map.MazeGenerator = map.maze_generator(self.config,
                                                          solve=True)
        self.crete_maze: game.GameState = game.generate_game_state(self.config)
        self.entry_cell: Cell = Cell(-1, -1)
        self.exit_cell: Cell = Cell(-1, -1)
        self.teseu_cell: Cell = Cell(-1, -1)
        self.minotaur_cell: Cell = Cell(-1, -1)
        self.margem_size: int = 0
        self.wall_size: int = 0
        self.cell_size: int = 0
        self.maze_pixel_width: int = 0
        self.maze_pixel_height: int = 0
        self.ptr: mlx.Mlx = mlx.Mlx()  # type: ignore
        self.mlx_ptr: mlx.Mlx = self.ptr.mlx_init()  # type: ignore
        self.win: mlx.Mlx | None = None
        self.state = State.DONE
        self.last_state = State.NOT_RESOLUTION
        self.generate_idx = 0
        self.resolution_idx = 0
        self.resolution_idx_t = 0
        self.resolution_idx_m = 0
        self.image: mlx.Mlx | None = None
        self.is_generate: bool = False
        self.data: bytearray = bytearray()
        self.size_line: int = 0
        self.path_color = 0x00CFFF
        self.maze_color = 0x111827
        self.pattern_color = 0x3B82F6
        self.background_color = 0x374151
        self.minotaur_image: mlx.Mlx | None = None
        self.minotaur_width: int = 0
        self.minotaur_height: int = 0
        self.teseu_image: mlx.Mlx | None = None
        self.teseu_width: int = 0
        self.teseu_height: int = 0
        self.teseu_victory: mlx.Mlx | None = None
        self.teseu_victory_width: int = 0
        self.teseu_victory_height: int = 0
        self.minotaur_victory: mlx.Mlx | None = None
        self.minotaur_victory_width: int = 0
        self.minotaur_victory_height: int = 0
        self.ariadne: bool = False

    def initialize_mlx(self) -> None:
        self.margem_size, self.wall_size, self.cell_size = (
            structure_dimensions(self.config))

        self.maze_pixel_width, self.maze_pixel_height = total_pixel_dimensions(
            self.config, self)

        self.image = self.ptr.mlx_new_image(
            self.mlx_ptr, self.maze_pixel_width,
            self.maze_pixel_height)  # type: ignore

        self.data, _, self.size_line, _ = self.ptr.mlx_get_data_addr(
            self.image)  # type: ignore

    def expose_hook(self, _: None) -> None:
        self.ptr.mlx_put_image_to_window(self.mlx_ptr,
                                         self.win, self.image,
                                         0, 0)  # type: ignore


def structure_dimensions(config: cfg) -> tuple[int, int, int]:
    margem_size = 5
    wall_size = 1 if config.width > 100 else 4
    base_cell_size = max(config.width, config.height)
    cell_size = (900 - (2 * margem_size) - (
        base_cell_size + 1) * wall_size) // base_cell_size
    return margem_size, wall_size, cell_size


def total_pixel_dimensions(config: cfg, mlx: MazeState) -> tuple[int, int]:

    pixel_width_wall = (config.width + 1) * mlx.wall_size
    pixel_height_wall = (config.height + 1) * mlx.wall_size
    pixel_cells_width = config.width * mlx.cell_size
    pixel_cells_height = config.height * mlx.cell_size
    maze_pixel_width = (
        pixel_width_wall + (2 * mlx.margem_size) + pixel_cells_width)
    maze_pixel_height = pixel_height_wall + (
        2 * mlx.margem_size) + pixel_cells_height

    return maze_pixel_width, maze_pixel_height


def put_pixel(app: MazeState, x: int, y: int, color: int) -> None:
    offset = (y * app.size_line) + (x * 4)
    if offset < 0 or offset + 4 > len(app.data):
        return
    app.data[offset:offset+4] = (0xFF000000 | color).to_bytes(4, 'little')


def draw_rect(app: MazeState, x: int, y: int,
              width: int, height: int, color: int) -> None:
    for i in range(x, x + width):
        if i >= app.maze_pixel_width or i < 0:
            continue
        for j in range(y, y + height):
            if j >= app.maze_pixel_height or j < 0:
                continue
            put_pixel(app, i, j, color)


def draw_cell(app: MazeState, cell: Cell, color: int) -> None:

    cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
    cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
    draw_rect(app, cx, cy, app.cell_size, app.cell_size, color)


def draw_minotaur(app: MazeState, cell: Cell) -> None:
    if app.minotaur_image is None:
        return
    cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
    cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
    cx += (app.cell_size - app.minotaur_width) // 2
    cy += (app.cell_size - app.minotaur_height) // 2
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.minotaur_image, cx, cy)  # type: ignore


def draw_teseu(app: MazeState, cell: Cell) -> None:
    if app.teseu_image is None:
        return
    cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
    cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
    cx += (app.cell_size - app.teseu_width) // 2
    cy += (app.cell_size - app.teseu_height) // 2
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.teseu_image, cx, cy)  # type: ignore


def draw_teseu_victory(app: MazeState, cell: Cell) -> None:
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.teseu_victory, 0, 0)  # type: ignore


def draw_minotaur_victory(app: MazeState, cell: Cell) -> None:
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.minotaur_victory, 0, 0)  # type: ignore


def draw_connection(app: MazeState, cell1: Cell,
                    cell2: Cell, color: int) -> None:

    cx1 = app.margem_size + cell1.x * (app.cell_size + app.wall_size)
    cy1 = app.margem_size + cell1.y * (app.cell_size + app.wall_size)

    if cell1.y > cell2.y:
        draw_rect(app, cx1, cy1 - app.wall_size, app.cell_size,
                  app.wall_size, color)

    if cell1.y < cell2.y:
        draw_rect(app, cx1, cy1 + app.cell_size, app.cell_size,
                  app.wall_size, color)

    if cell1.x > cell2.x:
        draw_rect(app, cx1 - app.wall_size, cy1, app.wall_size,
                  app.cell_size, color)

    if cell1.x < cell2.x:
        draw_rect(app, cx1 + app.cell_size, cy1, app.wall_size,
                  app.cell_size, color)


def draw_maze_cell(app: MazeState, cell: Cell, color: int) -> None:

    cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
    cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
    draw_cell(app, cell, color)

    if not cell.north:
        draw_rect(app, cx, cy - app.wall_size, app.cell_size,
                  app.wall_size, color)

    if not cell.south:
        draw_rect(app, cx, cy + app.cell_size, app.cell_size,
                  app.wall_size, color)

    if not cell.west:
        draw_rect(app, cx - app.wall_size, cy, app.wall_size,
                  app.cell_size, color)

    if not cell.east:
        draw_rect(app, cx + app.cell_size, cy, app.wall_size,
                  app.cell_size, color)


def draw_entry_exit(app: MazeState) -> None:
    draw_cell(app, app.entry_cell, 0x00FF00)
    draw_cell(app, app.exit_cell, 0xFF0000)


def draw_resolution_path(app: MazeState, color: int) -> None:
    for cell, cell1 in zip(app.maze.visited_cells_resolution,
                           app.maze.visited_cells_resolution[1:]):
        draw_cell(app, cell, color)
        draw_connection(app, cell, cell1, color)
    draw_entry_exit(app)
    app.expose_hook(None)


def draw_full_maze(app: MazeState, color: int) -> None:
    for cell in app.maze.visited_cells:
        draw_maze_cell(app, cell, color)

    draw_entry_exit(app)
    app.expose_hook(None)


def mino_teseu_position(app: MazeState) -> None:
    app.teseu_cell = app.crete_maze.teseu_pos
    app.minotaur_cell = app.crete_maze.minotaur_pos


def draw_full_maze_game(app: MazeState, color: int) -> None:
    for cell in app.crete_maze.maze.visited_cells:
        draw_maze_cell(app, cell, color)
    draw_cell(app, app.teseu_cell, 0x00FF00)
    draw_cell(app, app.exit_cell, 0xFF0000)
    app.expose_hook(None)


def loop_idle(_: None) -> None:
    pass


def generate(app: MazeState) -> None:
    if app.state != State.GENERATE:
        return
    app.entry_cell = app.maze.entry
    app.exit_cell = app.maze.exit
    cell = app.maze.visited_cells[app.generate_idx]
    draw_maze_cell(app, cell, app.maze_color)
    app.expose_hook(None)
    time.sleep(0.01)
    app.generate_idx += 1
    if app.generate_idx >= len(app.maze.visited_cells):
        draw_entry_exit(app)
        app.state = State.DONE
        app.last_state = State.NOT_RESOLUTION


def solve(app: MazeState) -> None:
    draw_entry_exit(app)
    cell = app.maze.visited_cells_resolution[app.resolution_idx]
    cell1 = app.maze.visited_cells_resolution[
        app.resolution_idx + 1] if app.resolution_idx + 1 < len(
            app.maze.visited_cells_resolution) else None
    if cell1 is None or app.state != State.RESOLUTION:
        app.state = State.DONE
        return
    draw_cell(app, cell, app.path_color)
    draw_connection(app, cell, cell1, app.path_color)
    app.expose_hook(None)
    time.sleep(0.01)
    app.resolution_idx += 1
    if app.resolution_idx >= len(
       app.maze.visited_cells_resolution) - 1:
        app.state = State.DONE
        app.last_state = State.RESOLUTION_SHOWN
        return


def change_color(app: MazeState) -> None:
    if not app.state == State.DONE:
        print("Cannot change color during animation.")
        return
    print("Changing the color...")
    app.maze_color = random.randint(0x800000, 0xAAAAAA)
    app.path_color = random.randint(0x444445, 0x799999)
    app.pattern_color = random.randint(0xCCCCCC, 0xFFFFFF)
    app.background_color = random.randint(0, 0x444444)
    draw_rect(app, 0, 0, app.maze_pixel_width,
              app.maze_pixel_height, app.background_color)

    if app.maze.visited_cells:
        for cell in app.maze.visited_cells:
            draw_maze_cell(app, cell, app.maze_color)

    for cell in app.maze.pattern_cells:
        draw_maze_cell(app, cell, app.pattern_color)

    if app.last_state == State.RESOLUTION_SHOWN:
        draw_resolution_path(app, app.path_color)
        draw_entry_exit(app)

    draw_entry_exit(app)
    app.expose_hook(None)


def show_hide_path(app: MazeState) -> None:
    if (app.state == State.DONE and
            app.last_state == State.RESOLUTION_SHOWN):
        app.state = State.RESOLUTION_HIDDEN
        app.last_state = State.RESOLUTION_HIDDEN
    elif (app.state == State.DONE and
            app.last_state == State.RESOLUTION_HIDDEN):
        app.state = State.RESOLUTION_SHOWN
        app.last_state = State.RESOLUTION_SHOWN
    elif app.last_state == State.NOT_RESOLUTION:
        print("The maze is not solved yet, cannot"
              " toggle resolution path.")
    else:
        print("You can only toggle the resolution path"
              " after the maze is solved.")
        return
    if app.state == State.RESOLUTION_HIDDEN:
        draw_rect(app, 0, 0, app.maze_pixel_width, app.maze_pixel_height,
                  app.background_color)
        for cell in app.maze.pattern_cells:
            draw_cell(app, cell, app.pattern_color)
        draw_full_maze(app, app.maze_color)
        app.state = State.DONE
        return

    elif app.state == State.RESOLUTION_SHOWN:
        draw_resolution_path(app, app.path_color)
        app.state = State.DONE
        return


def skip_animations(app: MazeState) -> None:
    if app.state == State.GENERATE:
        print("Skipping generation animation...")
        draw_full_maze(app, app.maze_color)
        app.state = State.DONE
        app.last_state = State.NOT_RESOLUTION
        return

    elif app.state == State.RESOLUTION:
        print("Skipping resolution animation...")
        draw_resolution_path(app, app.path_color)
        app.state = State.DONE
        app.last_state = State.RESOLUTION_SHOWN
        return


def key_hook(keycode: int, app: MazeState) -> None:
    if keycode == 65307:  # ESC
        app.ptr.mlx_loop_exit(app.mlx_ptr)  # type: ignore

    if keycode == 103:  # G
        if app.is_generate:
            print("A maze has already been generated.")
            return
        app.is_generate = True
        if app.state == State.GENERATE:
            print("The maze is already being generated.")
            return
        print("Generating the maze...")
        app.state = State.GENERATE
        app.maze = map.maze_generator(app.config, solve=True)
        app.ptr.mlx_loop_hook(app.mlx_ptr, generate, app)  # type: ignore

    if keycode == 114:  # R
        if not app.is_generate:
            print("You need to generate a maze before.")
            return
        print("Resetting the maze...")
        app.resolution_idx = 0
        app.generate_idx = 0
        app.maze.reset_visited()
        app.maze.visited_cells_resolution = []

        app.ptr.mlx_destroy_image(app.mlx_ptr, app.image)  # type: ignore
        app.initialize_mlx()

        draw_rect(app, 0, 0, app.maze_pixel_width,
                  app.maze_pixel_height, app.background_color)

        app.maze = map.maze_generator(app.config, solve=True)
        app.is_generate = True
        for cell in app.maze.pattern_cells:
            draw_cell(app, cell, app.pattern_color)

        draw_full_maze(app, app.maze_color)
        draw_entry_exit(app)
        app.expose_hook(None)
        app.state = State.DONE
        app.last_state = State.NOT_RESOLUTION
        app.ptr.mlx_loop_hook(app.mlx_ptr, loop_idle, None)  # type: ignore

    if keycode == 115:  # S
        if not app.is_generate:
            print("You need to generate a maze before.")
            return
        if app.state == State.RESOLUTION:
            print("The maze is already being solved.")
            return
        if not app.maze.visited_cells:
            print("Generate a maze first.")
            return
        if app.last_state != State.NOT_RESOLUTION:
            print("The maze is already solved.")
            return
        print("Solving the maze...")
        app.state = State.RESOLUTION
        app.ptr.mlx_loop_hook(app.mlx_ptr, solve, app)  # type: ignore
    if keycode == 99:  # C
        if not app.is_generate:
            print("You need to generate a maze before changing the color.")
            return
        print("Changing the color...")
        change_color(app)
    if keycode == 112:  # P
        if not app.is_generate:
            print("You need to generate a maze before.")
            return
        print("Hide/Show resolution path...")
        show_hide_path(app)
    if keycode == 32:  # SPACE
        if not app.is_generate:
            print("You need to generate a maze before.")
            return
        skip_animations(app)
    if keycode == 109:  # M
        if app.config.gamemode:
            print("Opening the game...")
            app.ptr.mlx_destroy_image(app.mlx_ptr, app.image)  # type: ignore
            app.ptr.mlx_destroy_window(app.mlx_ptr, app.win)  # type: ignore
            app.ptr.mlx_loop_exit(app.mlx_ptr)  # type: ignore
            app.state = State.GAME
        else:
            print("Game mode is not enabled in the configuration.")


def game_start(app: MazeState) -> None:
    if app.state == State.TESEU:
        app.crete_maze.teseu_path = (
                    app.crete_maze.maze.bfs_game(app.teseu_cell,
                                                 app.minotaur_cell)
                    )
        draw_entry_exit(app)
        cell1 = app.crete_maze.teseu_path[1] if len(
                app.crete_maze.teseu_path) > 1 else None

        if cell1 is None:
            app.state = State.DONE
            return
        draw_teseu(app, app.teseu_cell)
        app.teseu_cell = cell1
        if app.teseu_cell == app.minotaur_cell:
            print("Teseu reached the Minotaur!")
            app.state = State.PLAYER_MOVE
            app.minotaur_cell = app.exit_cell
            return
        draw_minotaur(app, app.minotaur_cell)
        app.expose_hook(None)

        draw_teseu(app, app.teseu_cell)

        draw_minotaur(app, app.minotaur_cell)

        time.sleep(0.05)
        app.crete_maze.teseu_idx += 1
        if app.crete_maze.teseu_idx % 2 != 0:
            return
        else:
            app.state = State.MINOTAUR
            return

    elif app.state == State.MINOTAUR:
        cell = app.crete_maze.minotaur_path[app.resolution_idx_m]
        cell1 = app.crete_maze.minotaur_path[
            app.resolution_idx_m + 1] if app.resolution_idx_m + 1 < len(
                app.crete_maze.minotaur_path) else None

        if cell == app.exit_cell:
            app.state = State.DONE
            print("Minotaur reached the exit! Teseu loses!")
            app.last_state = State.DONE
            app.ptr.mlx_destroy_image(app.mlx_ptr, app.image)  # type: ignore
            app.image = None
            draw_minotaur_victory(app, app.minotaur_cell)
            return
        if cell1 is None:
            app.state = State.DONE
            return

        draw_minotaur(app, cell)

        app.minotaur_cell = cell1
        draw_teseu(app, app.teseu_cell)
        app.expose_hook(None)
        draw_teseu(app, app.teseu_cell)
        draw_minotaur(app, app.minotaur_cell)
        time.sleep(0.05)
        app.resolution_idx_m += 1
        app.state = State.TESEU
        return


def move_teseu(app: MazeState, direction: str) -> None:
    if app.state != State.PLAYER_MOVE:
        return
    if direction == "up":
        next_cell = app.crete_maze.maze.get_cell(app.teseu_cell.x, app.teseu_cell.y - 1)
        if next_cell == (-1, -1) or next_cell.south:
            return
        
    elif direction == "down":
        next_cell = app.crete_maze.maze.get_cell(app.teseu_cell.x, app.teseu_cell.y + 1)
        if next_cell == (-1, -1) or next_cell.north:
            return
    elif direction == "left":
        next_cell = app.crete_maze.maze.get_cell(app.teseu_cell.x - 1, app.teseu_cell.y)
        if next_cell == (-1, -1) or next_cell.east:
            return
    elif direction == "right":
        next_cell = app.crete_maze.maze.get_cell(app.teseu_cell.x + 1, app.teseu_cell.y)
        if next_cell == (-1, -1) or next_cell.west:
            return
    else:
        return
    if next_cell == app.exit_cell:
        print("Teseu reached the exit! Teseu wins!")
        app.state = State.DONE
        app.last_state = State.DONE
        app.ptr.mlx_destroy_image(app.mlx_ptr, app.image)  # type: ignore
        app.image = None
        draw_teseu_victory(app, app.teseu_cell)
        return
    maze_cell = app.teseu_cell
    app.teseu_cell = next_cell
    draw_teseu(app, app.teseu_cell)
    draw_cell(app, maze_cell, app.maze_color)
    if app.ariadne:
        ariadne_path(app)
    app.expose_hook(None)
    draw_teseu(app, app.teseu_cell)
    app.ptr.mlx_loop_hook(app.mlx_ptr, loop_idle, None)  # type: ignore


def ariadne_path(app: MazeState) -> None:
    app.maze.visited_cells_resolution = []
    app.maze.visited_cells_resolution = (
        app.maze.bfs_game(app.teseu_cell,
                          app.exit_cell)
    )
    if app.ariadne:
        draw_resolution_path(app, 0xFFD700)


def key_game_hook(keycode: int, app: MazeState) -> None:
    if keycode == 65307:  # ESC
        print("Exiting the game...")
        if app.minotaur_image is not None:
            app.ptr.mlx_destroy_image(app.mlx_ptr,
                                      app.minotaur_image)  # type: ignore
            app.minotaur_image = None
        if app.image is not None:
            app.ptr.mlx_destroy_image(app.mlx_ptr, app.image)  # type: ignore
            app.image = None
        if app.teseu_image is not None:
            app.ptr.mlx_destroy_image(app.mlx_ptr,
                                      app.teseu_image)  # type: ignore
            app.teseu_image = None
        if app.teseu_victory is not None:
            app.ptr.mlx_destroy_image(app.mlx_ptr,
                                      app.teseu_victory)  # type: ignore
            app.teseu_victory = None
        if app.minotaur_victory is not None:
            app.ptr.mlx_destroy_image(app.mlx_ptr,
                                      app.minotaur_victory)  # type: ignore
            app.minotaur_victory = None
        app.ptr.mlx_destroy_window(app.mlx_ptr, app.win)  # type: ignore
        app.ptr.mlx_loop_exit(app.mlx_ptr)  # type: ignore
        app.state = State.DONE
    if keycode == 115:  # S
        print("Starting the game...")
        app.state = State.TESEU
        app.ptr.mlx_loop_hook(app.mlx_ptr, game_start, app)  # type: ignore
    if keycode in [65362, 65364, 65361, 65363]:
        if app.state == State.PLAYER_MOVE:
            if keycode == 65362:  # Up
                move_teseu(app, "up")
            elif keycode == 65364:  # Down
                move_teseu(app, "down")
            elif keycode == 65361:  # Left
                move_teseu(app, "left")
            elif keycode == 65363:  # Right
                move_teseu(app, "right")
    if keycode == 97:  # A
        if not app.ariadne:
            app.ariadne = True
        elif app.ariadne:
            draw_rect(app, 0, 0, app.maze_pixel_width, app.maze_pixel_height,
                      app.background_color)
            for cell in app.maze.pattern_cells:
                draw_cell(app, cell, app.pattern_color)
            draw_full_maze_game(app, app.maze_color)
            app.ariadne = False


def graphics(mode: str = "normal") -> None:

    sys.setrecursionlimit(300000)

    if mode == "game":
        app = MazeState()
        app.initialize_mlx()
        app.win = app.ptr.mlx_new_window(app.mlx_ptr, app.maze_pixel_width,
                                         app.maze_pixel_height,
                                         "Maze Game")  # type: ignore
        mino_teseu_position(app)
        app.maze_color = 0xC2B8A3
        app.background_color = 0x4A3F35
        app.path_color = 0xC9A227
        app.state = State.GAME
        for cell in app.maze.pattern_cells:
            draw_cell(app, cell, app.pattern_color)
        app.exit_cell = app.crete_maze.exit_pos
        app.crete_maze.minotaur_path = app.crete_maze.maze.bfs_game(
            app.minotaur_cell,
            app.exit_cell)
        (app.minotaur_image, app.minotaur_width,
         app.minotaur_height) = app.ptr.mlx_xpm_file_to_image(
                            app.mlx_ptr,
                            "baixados.xpm")  # type: ignore
        (app.teseu_image, app.teseu_width,
         app.teseu_height) = app.ptr.mlx_xpm_file_to_image(
                            app.mlx_ptr,
                            "teseu.xpm")  # type: ignore
        (app.teseu_victory, app.teseu_victory_width,
         app.teseu_victory_height) = app.ptr.mlx_xpm_file_to_image(
                            app.mlx_ptr,
                            "teseu_victory.xpm")  # type: ignore
        (app.minotaur_victory, app.minotaur_victory_width,
         app.minotaur_victory_height) = app.ptr.mlx_xpm_file_to_image(
                            app.mlx_ptr,
                            "mino.xpm")  # type: ignore
        draw_rect(app, 0, 0, app.maze_pixel_width,
                  app.maze_pixel_height, app.background_color)
        draw_full_maze_game(app, app.maze_color)
        app.ptr.mlx_key_hook(app.win, key_game_hook, app)  # type: ignore
        app.ptr.mlx_expose_hook(app.win, app.expose_hook, None)  # type: ignore
        app.ptr.mlx_loop_hook(app.mlx_ptr, loop_idle, None)  # type: ignore
        app.ptr.mlx_loop(app.mlx_ptr)  # type: ignore
        return
    app = MazeState()
    app.initialize_mlx()
    app.win = app.ptr.mlx_new_window(app.mlx_ptr, app.maze_pixel_width,
                                     app.maze_pixel_height,
                                     "Maze Generator")  # type: ignore
    draw_rect(app, 0, 0,
              app.maze_pixel_width, app.maze_pixel_height,
              app.background_color)

    for cell in app.maze.pattern_cells:
        draw_cell(app, cell, app.pattern_color)

    if app.state == State.DONE:
        app.ptr.mlx_loop_hook(app.mlx_ptr, loop_idle, None)  # type: ignore
    app.ptr.mlx_key_hook(app.win, key_hook, app)  # type: ignore
    app.ptr.mlx_expose_hook(app.win, app.expose_hook, None)  # type: ignore
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 300,
                           0xAAAAAA, "Press ESC to quit")  # type: ignore
    app.ptr.mlx_string_put(app.mlx_ptr, app.win,
                           900, 260, 0xAAAAAA,
                           "Press S to solve the maze")  # type: ignore
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 140, 0xAAAAAA,
                           "Press R to reset the maze")  # type: ignore
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 160, 0xAAAAAA,
                           "Press C to change the color")  # type: ignore
    app.ptr.mlx_string_put(app.mlx_ptr, app.win,
                           900, 180, 0xAAAAAA,
                           "Press P to hide/show"
                           "resolution path")  # type: ignore
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 280,
                           0xAAAAAA, "Press SPACE to"
                           "skip animations")  # type: ignore
    app.ptr.mlx_loop_hook(app.mlx_ptr, loop_idle, None)  # type: ignore
    app.ptr.mlx_loop(app.mlx_ptr)  # type: ignore

    if app.state == State.GAME:
        graphics(mode="game")


if __name__ == "__main__":
    graphics()
