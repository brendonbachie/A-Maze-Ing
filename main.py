import mlx
import time
import random
import validate_config
import map
from enum import Enum
import sys
#import game

class State(Enum):
    GENERATE = 1
    RESOLUTION = 2
    DONE = 3
    RESOLUTION_HIDDEN = 4
    RESOLUTION_SHOWN = 5
    NOT_RESOLUTION = 6

class MazeState():
    def __init__(self):
        self.config = None
        self.maze = None
        self.entry_cell = None
        self.exit_cell = None
        self.margem_size = None
        self.wall_size = None
        self.cell_size = None
        self.maze_pixel_width = None
        self.maze_pixel_height = None
        self.ptr = None
        self.mlx_ptr = None
        self.win = None
        self.state = State.GENERATE
        self.last_state = State.NOT_RESOLUTION
        self.generate_idx = 0
        self.resolution_idx = 0
        self.image = None
        self.data = None
        self.size_line = None
        self.path_color = 0x00CFFF
        self.maze_color = 0x111827
        self.pattern_color = 0x3B82F6
        self.background_color = 0x374151
        
    def initialize_maze(self):
        self.config = validate_config.read_config_file()
        self.maze = map.maze_generator(self.config)
        map.output_maze(self.maze)
        self.entry_cell = self.maze.get_cell(self.config.entry[0], self.config.entry[1])
        self.exit_cell = self.maze.get_cell(self.config.exit[0], self.config.exit[1])

    def initialize_mlx(self):
        self.margem_size, self.wall_size, self.cell_size = structure_dimensions(self.config)
        self.maze_pixel_width, self.maze_pixel_height = total_pixel_dimensions(self.config, self.margem_size, self.wall_size, self.cell_size)
        self.ptr, self.mlx_ptr, self.win = start_mlx(self.maze_pixel_width, self.maze_pixel_height)
        self.image = self.ptr.mlx_new_image(self.mlx_ptr, self.maze_pixel_width, self.maze_pixel_height)
        self.data, _, self.size_line, _ = self.ptr.mlx_get_data_addr(self.image)

def start_mlx(width, height) -> mlx.Mlx:
    ptr = mlx.Mlx()
    mlx_ptr = ptr.mlx_init()
    win = ptr.mlx_new_window(mlx_ptr, width + 500, height, "Maze Generator")
    return ptr, mlx_ptr, win

def structure_dimensions(config):
    margem_size = 10
    wall_size = 1 if config.width > 100 else 10
    base_cell_size = max(config.width, config.height)
    cell_size = (900 - (2 * margem_size) - (base_cell_size + 1) * wall_size) // base_cell_size
    return margem_size, wall_size, cell_size

def total_pixel_dimensions(config, margem_size, wall_size, cell_size):
    pixel_width_wall = (config.width + 1) * wall_size
    pixel_height_wall = (config.height + 1) * wall_size
    pixel_cells_width = config.width * cell_size
    pixel_cells_height = config.height * cell_size
    maze_pixel_width = pixel_width_wall + (2 * margem_size) + pixel_cells_width
    maze_pixel_height = pixel_height_wall + (2 * margem_size) + pixel_cells_height
    return maze_pixel_width, maze_pixel_height

def put_pixel(data, size_line, x, y, color):
    offset = (y * size_line) + (x * 4)
    if offset < 0 or offset + 4 > len(data):
        return
    data[offset:offset+4] = (0xFF000000 | color).to_bytes(4, 'little')

def draw_rect(data, size_line, x, y, width, height, color, total_pixel_width, total_pixel_height):
    for i in range(x, x + width):
        if i >= total_pixel_width or i < 0:
            continue
        for j in range(y, y + height):
            if j >= total_pixel_height or j < 0:
                continue
            put_pixel(data, size_line, i, j, color)

def draw_cell(data, size_line, cell, margem_size, wall_size, cell_size, color, total_pixel_width, total_pixel_height):
    cx = margem_size + cell.x * (cell_size + wall_size)
    cy = margem_size + cell.y * (cell_size + wall_size)
    draw_rect(data, size_line, cx, cy, cell_size, cell_size, color, total_pixel_width, total_pixel_height)

def draw_connection(data, size_line, cell1, cell2, margem_size, wall_size, cell_size, color, total_pixel_width, total_pixel_height):
    cx1 = margem_size + cell1.x * (cell_size + wall_size)
    cy1 = margem_size + cell1.y * (cell_size + wall_size)

    if cell1.y > cell2.y:
        draw_rect(data, size_line, cx1, cy1 - wall_size, cell_size, wall_size, color, total_pixel_width, total_pixel_height)
    if cell1.y < cell2.y:
        draw_rect(data, size_line, cx1, cy1 + cell_size, cell_size, wall_size, color, total_pixel_width, total_pixel_height)
    if cell1.x > cell2.x:
        draw_rect(data, size_line, cx1 - wall_size, cy1, wall_size, cell_size, color, total_pixel_width, total_pixel_height)
    if cell1.x < cell2.x:
        draw_rect(data, size_line, cx1 + cell_size, cy1, wall_size, cell_size, color, total_pixel_width, total_pixel_height)

def draw_maze_cell(data, size_line, cell, margem_size, wall_size, cell_size, color, total_pixel_width, total_pixel_height):
    cx = margem_size + cell.x * (cell_size + wall_size)
    cy = margem_size + cell.y * (cell_size + wall_size)
    draw_cell(data, size_line, cell, margem_size, wall_size, cell_size, color, total_pixel_width, total_pixel_height)
    if not cell.north:
        draw_rect(data, size_line, cx, cy - wall_size, cell_size, wall_size, color, total_pixel_width, total_pixel_height)
    if not cell.south:
        draw_rect(data, size_line, cx, cy + cell_size, cell_size, wall_size, color, total_pixel_width, total_pixel_height)
    if not cell.west:
        draw_rect(data, size_line, cx - wall_size, cy, wall_size, cell_size, color, total_pixel_width, total_pixel_height)
    if not cell.east:
        draw_rect(data, size_line, cx + cell_size, cy, wall_size, cell_size, color, total_pixel_width, total_pixel_height)

def draw_entry_exit(data, size_line, mazestate: MazeState, margem_size, wall_size, cell_size, total_pixel_width, total_pixel_height):
    cx_entry = margem_size + mazestate.entry_cell.x * (cell_size + wall_size)
    cy_entry = margem_size + mazestate.entry_cell.y * (cell_size + wall_size)
    cx_exit = margem_size + mazestate.exit_cell.x * (cell_size + wall_size)
    cy_exit = margem_size + mazestate.exit_cell.y * (cell_size + wall_size)
    draw_rect(data, size_line, cx_entry, cy_entry, cell_size, cell_size, 0x00FF00, total_pixel_width, total_pixel_height)
    draw_rect(data, size_line, cx_exit, cy_exit, cell_size, cell_size, 0xFF0000, total_pixel_width, total_pixel_height)

def draw_resolution_path(mazestate: MazeState, color):
    for cell, cell1 in zip(mazestate.maze.visited_cells_resolution, mazestate.maze.visited_cells_resolution[1:]):
        cx = mazestate.margem_size + cell.x * (mazestate.cell_size + mazestate.wall_size)
        cy = mazestate.margem_size + cell.y * (mazestate.cell_size + mazestate.wall_size)
        draw_rect(mazestate.data, mazestate.size_line, cx, cy, mazestate.cell_size, mazestate.cell_size, color, mazestate.maze_pixel_width, mazestate.maze_pixel_height)
        draw_connection(mazestate.data, mazestate.size_line, cell, cell1, mazestate.margem_size, mazestate.wall_size, mazestate.cell_size, color, mazestate.maze_pixel_width, mazestate.maze_pixel_height)
    draw_entry_exit(mazestate.data, mazestate.size_line, mazestate, mazestate.margem_size, mazestate.wall_size, mazestate.cell_size, mazestate.maze_pixel_width, mazestate.maze_pixel_height)
    mazestate.ptr.mlx_put_image_to_window(mazestate.mlx_ptr, mazestate.win, mazestate.image, 0, 0)

def draw_full_maze(app: MazeState, color):
    for cell in app.maze.visited_cells:
        draw_maze_cell(app.data, app.size_line, cell, app.margem_size, app.wall_size, app.cell_size, color, app.maze_pixel_width, app.maze_pixel_height)
    draw_entry_exit(app.data, app.size_line, app, app.margem_size, app.wall_size, app.cell_size, app.maze_pixel_width, app.maze_pixel_height)
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)

def main():

    sys.setrecursionlimit(300000)

    app = MazeState()
    app.initialize_maze()
    app.initialize_mlx()
    draw_rect(app.data, app.size_line, 0, 0, app.maze_pixel_width, app.maze_pixel_height, app.background_color, app.maze_pixel_width, app.maze_pixel_height)

    for cell in app.maze.pattern_cells:
        cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
        cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
        draw_rect(app.data, app.size_line, cx, cy, app.cell_size, app.cell_size, app.pattern_color, app.maze_pixel_width, app.maze_pixel_height)



    def update(param):

        if app.state == State.GENERATE:
            cell = app.maze.visited_cells[app.generate_idx]
            draw_maze_cell(app.data, app.size_line, cell, app.margem_size, app.wall_size, app.cell_size, app.maze_color, app.maze_pixel_width, app.maze_pixel_height)
            app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)
            time.sleep(0.01)
            app.generate_idx += 1
            if app.generate_idx >= len(app.maze.visited_cells):
                app.state = State.DONE
                app.last_state = State.NOT_RESOLUTION
            draw_entry_exit(app.data, app.size_line, app, app.margem_size, app.wall_size, app.cell_size, app.maze_pixel_width, app.maze_pixel_height)
            return

        elif app.state == State.RESOLUTION:
            draw_entry_exit(app.data, app.size_line, app, app.margem_size, app.wall_size, app.cell_size, app.maze_pixel_width, app.maze_pixel_height)
            cell = app.maze.visited_cells_resolution[app.resolution_idx]
            cell1 = app.maze.visited_cells_resolution[app.resolution_idx + 1] if app.resolution_idx + 1 < len(app.maze.visited_cells_resolution) else None
            if cell1 is None:
                app.state = State.DONE
                return
            cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
            cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
            draw_rect(app.data, app.size_line, cx, cy, app.cell_size, app.cell_size, app.path_color, app.maze_pixel_width, app.maze_pixel_height)
            
            draw_connection(app.data, app.size_line, cell, cell1, app.margem_size, app.wall_size, app.cell_size, app.path_color, app.maze_pixel_width, app.maze_pixel_height)
            
            app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)
            time.sleep(0.01)
            app.resolution_idx += 1
            if app.resolution_idx >= len(app.maze.visited_cells_resolution) - 1:
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

    def key_options(keycode, param):

        if keycode == 65307:  # ESC
            app.ptr.mlx_loop_exit(app.mlx_ptr)

        if keycode == 114:  # R
            print("Resetting the maze...")
            app.maze = map.maze_generator(app.config)
            app.entry_cell = app.maze.get_cell(app.config.entry[0], app.config.entry[1])
            app.exit_cell = app.maze.get_cell(app.config.exit[0], app.config.exit[1])
            app.ptr.mlx_destroy_image(app.mlx_ptr, app.image)
            app.image = app.ptr.mlx_new_image(app.mlx_ptr, app.maze_pixel_width, app.maze_pixel_height)
            app.data, _, app.size_line, _ = app.ptr.mlx_get_data_addr(app.image)
            draw_rect(app.data, app.size_line, 0, 0, app.maze_pixel_width, app.maze_pixel_height, app.background_color, app.maze_pixel_width, app.maze_pixel_height)
            for cell in app.maze.pattern_cells:
                draw_maze_cell(app.data, app.size_line, cell, app.margem_size, app.wall_size, app.cell_size, app.pattern_color, app.maze_pixel_width, app.maze_pixel_height)
            app.state = State.GENERATE
            app.last_state = State.NOT_RESOLUTION
            app.generate_idx = 0
            app.resolution_idx = 0

        if keycode == 99:  # C
            if not app.state == State.DONE:
                print("Cannot change color during animation.")
                return
            print("Changing the color...")
            app.maze_color = random.randint(0, 0xFFFFFF)
            app.path_color = random.randint(0, 0xFFFFFF)
            app.pattern_color = random.randint(0, 0xFFFFFF)
            for cell in app.maze.visited_cells:
                draw_maze_cell(app.data, app.size_line, cell, app.margem_size, app.wall_size, app.cell_size, app.maze_color, app.maze_pixel_width, app.maze_pixel_height)

            for cell in app.maze.pattern_cells:
                cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
                cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
                draw_rect(app.data, app.size_line, cx, cy, app.cell_size, app.cell_size, app.pattern_color, app.maze_pixel_width, app.maze_pixel_height)

            if app.last_state == State.RESOLUTION_SHOWN and not app.last_state == State.NOT_RESOLUTION:
                draw_resolution_path(app, app.path_color)
                draw_entry_exit(app.data, app.size_line, app, app.margem_size, app.wall_size, app.cell_size, app.maze_pixel_width, app.maze_pixel_height)
            app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)

        if keycode == 112:  # P
            print("Hide/Show resolution path...")
            if app.state == State.DONE and app.last_state == State.RESOLUTION_SHOWN:
                app.state = State.RESOLUTION_HIDDEN
                app.last_state = State.RESOLUTION_HIDDEN
            elif app.state == State.DONE and app.last_state == State.RESOLUTION_HIDDEN:
                app.state = State.RESOLUTION_SHOWN
                app.last_state = State.RESOLUTION_SHOWN
            elif app.last_state == State.NOT_RESOLUTION:
                print("The maze is not solved yet, cannot toggle resolution path.")
            else:
                print("You can only toggle the resolution path after the maze is solved.")
        if keycode == 115:  # S
            if app.state == State.DONE and app.last_state == State.NOT_RESOLUTION:
                print("Solving the maze")
                app.state = State.RESOLUTION
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
                
    app.ptr.mlx_key_hook(app.win, key_options, None)
    def expose_hook(param):
        app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)
    app.ptr.mlx_expose_hook(app.win, expose_hook, None)


    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 300, 0xAAAAAA, "Press ESC to quit")
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 260, 0xAAAAAA, "Press S to solve the maze")
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 140, 0xAAAAAA, "Press R to reset the maze")
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 160, 0xAAAAAA, "Press C to change the color")
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 180, 0xAAAAAA, "Press P to hide/show resolution path")
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 280, 0xAAAAAA, "Press SPACE to skip animations")

    app.ptr.mlx_loop_hook(app.mlx_ptr, update, None)


    app.ptr.mlx_loop(app.mlx_ptr)

if __name__ == "__main__":
    main()