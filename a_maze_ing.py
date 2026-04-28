import sys
import draw
import state
import hooks


def graphics(mode: str = "normal") -> None:

    sys.setrecursionlimit(300000)

    if mode == "game":
        app = state.MazeState()
        app.initialize_mlx()
        app.win = app.ptr.mlx_new_window(app.mlx_ptr, app.maze_pixel_width,
                                         app.maze_pixel_height,
                                         "Maze Game")  # type: ignore
        hooks.mino_teseu_position(app)
        app.maze_color = 0xC2B8A3
        app.background_color = 0x4A3F35
        app.path_color = 0xC9A227
        app.state = state.State.GAME
        for cell in app.maze.pattern_cells:
            draw.draw_cell(app, cell, app.pattern_color)
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
        draw.draw_rect(app, 0, 0, app.maze_pixel_width,
                       app.maze_pixel_height, app.background_color)
        draw.draw_full_maze_game(app, app.maze_color)
        app.ptr.mlx_key_hook(app.win, hooks.key_game_hook, app)  # type: ignore
        app.ptr.mlx_expose_hook(app.win, app.expose_hook, None)  # type: ignore
        app.ptr.mlx_loop_hook(app.mlx_ptr, draw.loop_idle, None)  # type:ignore
        app.ptr.mlx_loop(app.mlx_ptr)  # type: ignore
        return
    app = state.MazeState()
    app.initialize_mlx()
    app.win = app.ptr.mlx_new_window(app.mlx_ptr, app.maze_pixel_width,
                                     app.maze_pixel_height,
                                     "Maze Generator")  # type: ignore
    draw.draw_rect(app, 0, 0,
                   app.maze_pixel_width, app.maze_pixel_height,
                   app.background_color)

    for cell in app.maze.pattern_cells:
        draw.draw_cell(app, cell, app.pattern_color)

    if app.state == state.State.DONE:
        app.ptr.mlx_loop_hook(app.mlx_ptr, draw.loop_idle, None)  # type:ignore
    app.ptr.mlx_key_hook(app.win, hooks.key_hook, app)  # type: ignore
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
    app.ptr.mlx_loop_hook(app.mlx_ptr, draw.loop_idle, None)  # type: ignore
    app.ptr.mlx_loop(app.mlx_ptr)  # type: ignore

    if app.state == state.State.GAME:
        graphics(mode="game")


if __name__ == "__main__":
    graphics()
