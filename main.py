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


class MazeState():
    def __init__(self) -> None:
        self.config: cfg = validate_config.read_config_file()
        self.maze: map.MazeGenerator = map.maze_generator(self.config)
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
        self.state = State.GAME
        self.last_state = State.NOT_RESOLUTION
        self.generate_idx = 0
        self.resolution_idx = 0
        self.resolution_idx_t = 0
        self.resolution_idx_m = 0
        self.image: mlx.Mlx | None = None
        self.data: bytearray = bytearray()
        self.size_line: int = 0
        self.path_color = 0x00CFFF
        self.maze_color = 0x111827
        self.pattern_color = 0x3B82F6
        self.background_color = 0x374151

    def initialize_maze(self) -> None:
        map.output_maze(self.maze)
        self.entry_cell = self.maze.entry
        self.exit_cell = self.maze.exit

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
    app.ptr.mlx_put_image_to_window(
        app.mlx_ptr, app.win,
        app.image, 0, 0)  # type: ignore


def draw_full_maze(app: MazeState, color: int) -> None:
    for cell in app.maze.visited_cells:
        draw_maze_cell(app, cell, color)

    draw_entry_exit(app)
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.image, 0, 0)  # type: ignore


def draw_full_maze_game(app: MazeState, color: int) -> None:
    for cell in app.crete_maze.maze.visited_cells:
        draw_maze_cell(app, cell, color)
    draw_cell(app, app.teseu_cell, 0x00FF00)
    draw_cell(app, app.exit_cell, 0xFF0000)
    draw_cell(app, app.minotaur_cell, 0xFFFF00)
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.image, 0, 0)  # type: ignore


def main() -> None:

    sys.setrecursionlimit(300000)

    app = MazeState()
    app.initialize_maze()
    app.win = app.ptr.mlx_new_window(app.mlx_ptr, app.maze_pixel_width,
                                     app.maze_pixel_height,
                                     "Maze Generator")  # type: ignore
    draw_rect(app, 0, 0,
              app.maze_pixel_width, app.maze_pixel_height,
              app.background_color)

    def initialize_game_maze(app: MazeState) -> None:
        app.teseu_cell = app.crete_maze.teseu_pos
        app.minotaur_cell = app.crete_maze.minotaur_pos

    def expose_hook(_: None) -> None:
        app.ptr.mlx_put_image_to_window(app.mlx_ptr,
                                        app.win, app.image,
                                        0, 0)  # type: ignore

    for cell in app.maze.pattern_cells:
        draw_cell(app, cell, app.pattern_color)
    initialize_game_maze(app)

    # app.crete_maze.minotaur_path =
    # app.crete_maze.maze.bfs_game(app.minotaur_cell, app.exit_cell)
    def update(_: None) -> None:

        if app.state == State.GENERATE:
            cell = app.maze.visited_cells[app.generate_idx]
            draw_maze_cell(app, cell, app.maze_color)

            expose_hook(None)
            time.sleep(0.01)
            app.generate_idx += 1
            if app.generate_idx >= len(app.maze.visited_cells):
                app.state = State.DONE
                app.last_state = State.NOT_RESOLUTION
            draw_entry_exit(app)
            return

        elif app.state == State.RESOLUTION:
            draw_entry_exit(app)

            cell = app.maze.visited_cells_resolution[app.resolution_idx]
            cell1 = app.maze.visited_cells_resolution[
                app.resolution_idx + 1] if app.resolution_idx + 1 < len(
                    app.maze.visited_cells_resolution) else None
            if cell1 is None:
                app.state = State.DONE
                return
            draw_cell(app, cell, app.path_color)

            draw_connection(app, cell, cell1, app.path_color)

            expose_hook(None)
            time.sleep(0.01)
            app.resolution_idx += 1
            if app.resolution_idx >= len(
               app.maze.visited_cells_resolution) - 1:
                app.state = State.DONE
                app.last_state = State.RESOLUTION_SHOWN
                return

        elif app.state == State.DONE:
            return

        elif app.state == State.RESOLUTION_HIDDEN:
            draw_full_maze(app, app.maze_color)
            app.state = State.DONE
            return

        elif app.state == State.RESOLUTION_SHOWN:
            draw_resolution_path(app, app.path_color)
            app.state = State.DONE
            return

        elif app.state == State.GAME:
            initialize_game_maze(app)
            draw_full_maze_game(app, app.maze_color)
            app.state = State.DONE
            return

        elif app.state == State.TESEU:
            app.crete_maze.teseu_path = (
                app.crete_maze.maze.bfs_game(app.teseu_cell, app.minotaur_cell)
                )

            draw_entry_exit(app)

            cell = app.crete_maze.teseu_path[app.resolution_idx_t]
            cell1 = app.crete_maze.teseu_path[
                app.resolution_idx_t + 1] if app.resolution_idx_t + 1 < len(
                    app.crete_maze.teseu_path) else None

            if cell == app.minotaur_cell:
                print("Teseu reached the Minotaur!")
                app.state = State.DONE
                return
            if cell1 is None:
                app.state = State.DONE
                return
            draw_cell(app, cell, 0xFFFF00)

            draw_cell(app, cell1, 0xFFFF00)

            draw_maze_cell(app, cell, app.maze_color)

            # printar a conexao
            # draw_connection(app.data, app.size_line, cell, cell1,
            # app.margem_size, app.wall_size, app.cell_size, app.path_color,
            # app.maze_pixel_width, app.maze_pixel_height)

            expose_hook(None)
            time.sleep(0.01)
            app.crete_maze.teseu_idx += 1
            if app.crete_maze.teseu_idx % 2 != 0:
                app.resolution_idx_t += 1
                return
            else:
                app.resolution_idx_t += 1
                app.state = State.MINOTAUR
            # if app.resolution_idx_t >= len(app.crete_maze.teseu_path) - 1:
            #     app.state = State.DONE
            #     app.last_state = State.RESOLUTION_SHOWN
            #     return
            return

        elif app.state == State.MINOTAUR:
            # app.crete_maze.minotaur_path = app.crete_maze.maze.bfs_game(
            # app.minotaur_cell, app.exit_cell)
            draw_entry_exit(app)

            cell = app.crete_maze.minotaur_path[app.resolution_idx_m]
            cell1 = app.crete_maze.minotaur_path[
                app.resolution_idx_m + 1] if app.resolution_idx_m + 1 < len(
                    app.crete_maze.minotaur_path) else None

            if cell == app.exit_cell:
                app.state = State.DONE
                app.last_state = State.RESOLUTION_SHOWN
                return
            if cell1 is None:
                app.state = State.DONE
                return

            draw_cell(app, cell, app.path_color)

            draw_cell(app, cell1, app.path_color)

            draw_maze_cell(app, cell, app.maze_color)

            # printar a conexao
            # draw_connection(app.data, app.size_line, cell, cell1,
            # app.margem_size, app.wall_size, app.cell_size, app.path_color,
            # app.maze_pixel_width, app.maze_pixel_height)

            app.minotaur_cell = cell1
            expose_hook(None)
            time.sleep(0.01)
            app.resolution_idx_m += 1
            app.crete_maze.minotaur_idx += 1
            if app.crete_maze.minotaur_idx < 10:
                app.state = State.TESEU
                return
            # if app.resolution_idx_t >= len(app.crete_maze.minotaur_path) - 1:
            #     app.state = State.DONE
            #     app.last_state = State.RESOLUTION_SHOWN
            #     return
            app.crete_maze.maze.bfs_game(app.minotaur_cell, app.exit_cell)
            app.state = State.TESEU
            return

    def key_options(keycode: int, _: None) -> None:

        if keycode == 65307:  # ESC
            app.ptr.mlx_loop_exit(app.mlx_ptr)  # type: ignore

        if keycode == 114:  # R
            print("Resetting the maze...")
            app.maze = map.maze_generator(app.config)
            app.entry_cell = app.maze.get_cell(
                app.config.entry[0], app.config.entry[1])

            app.exit_cell = app.maze.get_cell(
                app.config.exit[0], app.config.exit[1])

            app.ptr.mlx_destroy_image(app.mlx_ptr, app.image)  # type: ignore

            app.image = app.ptr.mlx_new_image(
                app.mlx_ptr,
                app.maze_pixel_width, app.maze_pixel_height)  # type: ignore

            app.data, _, app.size_line, _ = app.ptr.mlx_get_data_addr(
                app.image)  # type: ignore

            draw_rect(app, 0, 0, app.maze_pixel_width,
                      app.maze_pixel_height, app.background_color)

            for cell in app.maze.pattern_cells:
                draw_maze_cell(app, cell, app.pattern_color)
            app.state = State.GENERATE
            app.last_state = State.NOT_RESOLUTION
            app.generate_idx = 0
            app.resolution_idx = 0

        if keycode == 99:  # C
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

            for cell in app.maze.visited_cells:
                draw_maze_cell(app, cell, app.maze_color)

            for cell in app.maze.pattern_cells:
                draw_maze_cell(app, cell, app.pattern_color)

            if app.last_state == State.RESOLUTION_SHOWN:
                draw_resolution_path(app, app.path_color)
                draw_entry_exit(app)

            expose_hook(None)

        if keycode == 112:  # P
            print("Hide/Show resolution path...")
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
        if keycode == 115:  # S
            if (app.state == State.DONE and
                    app.last_state == State.NOT_RESOLUTION):
                print("Solving the maze")
                app.state = State.TESEU
                app.resolution_idx = 0

        if keycode == 32:  # SPACE
            if app.state == State.GENERATE:
                print("Skipping generation animation...")
                draw_full_maze(app, app.maze_color)
                app.state = State.DONE
                app.last_state = State.NOT_RESOLUTION

            elif app.state == State.RESOLUTION:
                print("Skipping resolution animation...")
                draw_resolution_path(app, app.path_color)
                app.state = State.DONE
                app.last_state = State.RESOLUTION_SHOWN

    app.ptr.mlx_key_hook(app.win, key_options, None)  # type: ignore
    app.ptr.mlx_expose_hook(app.win, expose_hook, None)  # type: ignore

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

    app.ptr.mlx_loop_hook(app.mlx_ptr, update, None)  # type: ignore

    app.ptr.mlx_loop(app.mlx_ptr)  # type: ignore


if __name__ == "__main__":
    main()
