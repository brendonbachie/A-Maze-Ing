from map import Cell
from state import MazeState
from validate_config import Configuration as cfg


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


def draw_resolution_path_game(app: MazeState, color: int) -> None:
    for cell, cell1 in zip(app.crete_maze.maze.visited_cells_resolution,
                           app.crete_maze.maze.visited_cells_resolution[1:]):
        draw_cell(app, cell, color)
        draw_connection(app, cell, cell1, color)
    draw_cell(app, app.exit_cell, 0xFF0000)
    app.expose_hook(None)


def draw_full_maze(app: MazeState, color: int) -> None:
    for cell in app.maze.visited_cells:
        draw_maze_cell(app, cell, color)

    draw_entry_exit(app)
    app.expose_hook(None)


def draw_full_maze_game(app: MazeState, color: int) -> None:
    for cell in app.crete_maze.maze.visited_cells:
        draw_maze_cell(app, cell, color)
    draw_cell(app, app.teseu_cell, 0x00FF00)
    draw_cell(app, app.exit_cell, 0xFF0000)
    app.expose_hook(None)


def loop_idle(_: None) -> None:
    pass
