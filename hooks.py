import draw
import time
import random
import map
from state import MazeState, State


def mino_teseu_position(app: MazeState) -> None:
    app.teseu_cell = app.crete_maze.teseu_pos
    app.minotaur_cell = app.crete_maze.minotaur_pos


def generate(app: MazeState) -> None:
    if app.state != State.GENERATE:
        return
    app.entry_cell = app.maze.entry
    app.exit_cell = app.maze.exit
    cell = app.maze.visited_cells[app.generate_idx]
    draw.draw_maze_cell(app, cell, app.maze_color)
    app.expose_hook(None)
    time.sleep(0.01)
    app.generate_idx += 1
    if app.generate_idx >= len(app.maze.visited_cells):
        draw.draw_entry_exit(app)
        app.state = State.DONE
        app.last_state = State.NOT_RESOLUTION


def solve(app: MazeState) -> None:
    draw.draw_entry_exit(app)
    cell = app.maze.visited_cells_resolution[app.resolution_idx]
    cell1 = app.maze.visited_cells_resolution[
        app.resolution_idx + 1] if app.resolution_idx + 1 < len(
            app.maze.visited_cells_resolution) else None
    if cell1 is None or app.state != State.RESOLUTION:
        app.state = State.DONE
        return
    draw.draw_cell(app, cell, app.path_color)
    draw.draw_connection(app, cell, cell1, app.path_color)
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
    draw.draw_rect(app, 0, 0, app.maze_pixel_width,
                   app.maze_pixel_height, app.background_color)

    if app.maze.visited_cells:
        for cell in app.maze.visited_cells:
            draw.draw_maze_cell(app, cell, app.maze_color)

    for cell in app.maze.pattern_cells:
        draw.draw_maze_cell(app, cell, app.pattern_color)

    if app.last_state == State.RESOLUTION_SHOWN:
        draw.draw_resolution_path(app, app.path_color)
        draw.draw_entry_exit(app)

    draw.draw_entry_exit(app)
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
        draw.draw_rect(app, 0, 0, app.maze_pixel_width, app.maze_pixel_height,
                       app.background_color)
        for cell in app.maze.pattern_cells:
            draw.draw_cell(app, cell, app.pattern_color)
        draw.draw_full_maze(app, app.maze_color)
        app.state = State.DONE
        return

    elif app.state == State.RESOLUTION_SHOWN:
        draw.draw_resolution_path(app, app.path_color)
        app.state = State.DONE
        return


def skip_animations(app: MazeState) -> None:
    if app.state == State.GENERATE:
        print("Skipping generation animation...")
        draw.draw_full_maze(app, app.maze_color)
        app.state = State.DONE
        app.last_state = State.NOT_RESOLUTION
        return

    elif app.state == State.RESOLUTION:
        print("Skipping resolution animation...")
        draw.draw_resolution_path(app, app.path_color)
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
        app.maze.generate(True)
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

        draw.draw_rect(app, 0, 0, app.maze_pixel_width,
                       app.maze_pixel_height, app.background_color)

        app.maze = map.MazeGenerator(app.config)
        app.maze.generate(True)
        app.is_generate = True
        for cell in app.maze.pattern_cells:
            draw.draw_cell(app, cell, app.pattern_color)

        draw.draw_full_maze(app, app.maze_color)
        draw.draw_entry_exit(app)
        app.expose_hook(None)
        app.state = State.DONE
        app.last_state = State.NOT_RESOLUTION
        app.ptr.mlx_loop_hook(app.mlx_ptr, draw.loop_idle, None)  # type:ignore

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
        draw.draw_entry_exit(app)
        cell1 = app.crete_maze.teseu_path[1] if len(
                app.crete_maze.teseu_path) > 1 else None

        if cell1 is None:
            app.state = State.DONE
            return
        draw.draw_teseu(app, app.teseu_cell)
        app.teseu_cell = cell1
        if app.teseu_cell == app.minotaur_cell:
            print("Teseu reached the Minotaur!")
            app.state = State.PLAYER_MOVE
            app.ptr.mlx_loop_hook(app.mlx_ptr,
                                  draw.loop_idle, None)  # type: ignore
            return
        draw.draw_minotaur(app, app.minotaur_cell)
        app.expose_hook(None)

        draw.draw_teseu(app, app.teseu_cell)

        draw.draw_minotaur(app, app.minotaur_cell)

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
            draw.draw_minotaur_victory(app, app.minotaur_cell)
            return
        if cell1 is None:
            app.state = State.DONE
            return
        if cell == app.teseu_cell:
            print("Teseu reached the Minotaur!")
            app.state = State.PLAYER_MOVE
            return
        draw.draw_minotaur(app, cell)

        app.minotaur_cell = cell1
        draw.draw_teseu(app, app.teseu_cell)
        app.expose_hook(None)
        draw.draw_teseu(app, app.teseu_cell)
        draw.draw_minotaur(app, app.minotaur_cell)
        time.sleep(0.05)
        app.resolution_idx_m += 1
        app.state = State.TESEU
        return


def ariadne_path(app: MazeState) -> None:
    app.crete_maze.maze.visited_cells_resolution = []
    app.crete_maze.maze.visited_cells_resolution = (
        app.crete_maze.maze.bfs_game(app.teseu_cell,
                                     app.exit_cell)
    )
    if app.ariadne:
        draw.draw_resolution_path_game(app, 0xFFD700)


def move_teseu(app: MazeState, direction: str) -> None:
    if app.state != State.PLAYER_MOVE:
        return
    if direction == "up":
        next_cell = app.crete_maze.maze.get_cell(app.teseu_cell.x,
                                                 app.teseu_cell.y - 1)
        if next_cell == (-1, -1) or next_cell.south:
            return

    elif direction == "down":
        next_cell = app.crete_maze.maze.get_cell(app.teseu_cell.x,
                                                 app.teseu_cell.y + 1)
        if next_cell == (-1, -1) or next_cell.north:
            return
    elif direction == "left":
        next_cell = app.crete_maze.maze.get_cell(app.teseu_cell.x - 1,
                                                 app.teseu_cell.y)
        if next_cell == (-1, -1) or next_cell.east:
            return
    elif direction == "right":
        next_cell = app.crete_maze.maze.get_cell(app.teseu_cell.x + 1,
                                                 app.teseu_cell.y)
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
        draw.draw_teseu_victory(app, app.teseu_cell)
        return
    maze_cell = app.teseu_cell
    app.teseu_cell = next_cell
    draw.draw_teseu(app, app.teseu_cell)
    draw.draw_cell(app, maze_cell, app.maze_color)
    if app.ariadne:
        ariadne_path(app)
        draw.draw_connection(app, maze_cell, app.teseu_cell, app.maze_color)

    app.expose_hook(None)
    draw.draw_teseu(app, app.teseu_cell)
    app.ptr.mlx_loop_hook(app.mlx_ptr, draw.loop_idle, None)  # type: ignore


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
            draw.draw_rect(
                app,
                0,
                0,
                app.maze_pixel_width,
                app.maze_pixel_height,
                app.background_color,
            )
            for cell in app.maze.pattern_cells:
                draw.draw_cell(app, cell, app.pattern_color)
            draw.draw_full_maze_game(app, app.maze_color)
            app.ariadne = False
