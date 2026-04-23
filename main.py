import time
import random
import mlx
import validate_config
import map
from enum import Enum

class State(Enum):
    GENERATE = 1
    RESOLUTION = 2
    DONE = 3
    RESOLUTION_HIDDEN = 4
    RESOLUTION_SHOWN = 5

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
        self.generate_idx = 0
        self.resolution_idx = 0
        self.image = None
        self.data = None
        self.size_line = None
        
    def initialize(self):
        self.config = validate_config.read_config_file()
        self.maze = maze_generator(self.config)
        map.output_maze(self.maze)
        self.margem_size, self.wall_size, self.cell_size = structure_dimensions(self.config)
        self.maze_pixel_width, self.maze_pixel_height = total_pixel_dimensions(self.config, self.margem_size, self.wall_size, self.cell_size)
        self.ptr, self.mlx_ptr, self.win = start_mlx(self.maze_pixel_width, self.maze_pixel_height)
        self.entry_cell = self.maze.get_cell(self.config.entry[0], self.config.entry[1])
        self.exit_cell = self.maze.get_cell(self.config.exit[0], self.config.exit[1])
        self.image = self.ptr.mlx_new_image(self.mlx_ptr, self.maze_pixel_width, self.maze_pixel_height)
        self.data, _, self.size_line, _ = self.ptr.mlx_get_data_addr(self.image)

def maze_generator(config) -> map.MazeGenerator:
    maze = map.MazeGenerator(config)
    if maze.width < 8 or maze.height < 8:
        print("The maze is too small to apply the pattern, skipping it...")
    else:
        maze.pattern()
    maze.dfs(maze.maze[0])
    if not config.perfect:
        maze.not_perfect_maze()
    maze.reset_visited()
    entry_cell = maze.get_cell(config.entry[0], config.entry[1])
    exit_cell = maze.get_cell(config.exit[0], config.exit[1])
    maze.bfs_resolution(entry_cell, exit_cell)
    return maze

def start_mlx(width, height) -> mlx.Mlx:
    ptr = mlx.Mlx()
    mlx_ptr = ptr.mlx_init()
    win = ptr.mlx_new_window(mlx_ptr, width + 500, height, "Maze Generator")
    return ptr, mlx_ptr, win

def structure_dimensions(config):
    margem_size = 10
    wall_size = 5 if config.width > 39 else 10
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
    
def main():

    app = MazeState()
    app.initialize()
    draw_rect(app.data, app.size_line, 0, 0, app.maze_pixel_width, app.maze_pixel_height, 0x374151, app.maze_pixel_width, app.maze_pixel_height)

    for cell in app.maze.pattern_cells:
        cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
        cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
        draw_rect(app.data, app.size_line, cx, cy, app.cell_size, app.cell_size, 0x3B82F6, app.maze_pixel_width, app.maze_pixel_height)



    def update(param):

        if app.state == State.GENERATE:
            for cell in app.maze.visited_cells:
                draw_maze_cell(app.data, app.size_line, cell, app.margem_size, app.wall_size, app.cell_size, 0x111827, app.maze_pixel_width, app.maze_pixel_height)
                app.generate_idx += 1

            app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)

            app.state = State.DONE
            return

        elif app.state == State.RESOLUTION:
            draw_rect(app.data, app.size_line, app.entry_cell.x * (app.cell_size + app.wall_size) + app.margem_size, app.entry_cell.y * (app.cell_size + app.wall_size) + app.margem_size, app.cell_size, app.cell_size, 0x00FF00, app.maze_pixel_width, app.maze_pixel_height)
            draw_rect(app.data, app.size_line, app.exit_cell.x * (app.cell_size + app.wall_size) + app.margem_size, app.exit_cell.y * (app.cell_size + app.wall_size) + app.margem_size, app.cell_size, app.cell_size, 0xFF0000, app.maze_pixel_width, app.maze_pixel_height)
            cell = app.maze.visited_cells_resolution[app.resolution_idx]
            cell1 = app.maze.visited_cells_resolution[app.resolution_idx + 1] if app.resolution_idx + 1 < len(app.maze.visited_cells_resolution) else None
            if cell1 is None:
                app.state = State.DONE
                return
            cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
            cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
            draw_rect(app.data, app.size_line, cx, cy, app.cell_size, app.cell_size, 0x00CFFF, app.maze_pixel_width, app.maze_pixel_height)
            
            draw_connection(app.data, app.size_line, cell, cell1, app.margem_size, app.wall_size, app.cell_size, 0x00CFFF, app.maze_pixel_width, app.maze_pixel_height)
            
            app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)
            time.sleep(0.01)
            app.resolution_idx += 1
            if app.resolution_idx >= len(app.maze.visited_cells_resolution) - 1:
                app.state = State.DONE
                return
            
        elif app.state == State.DONE:
            return
        
        elif app.state == State.RESOLUTION_HIDDEN:
            for cell in app.maze.visited_cells_resolution:
                draw_rect(app.data, app.size_line, app.entry_cell.x * (app.cell_size + app.wall_size) + app.margem_size, app.entry_cell.y * (app.cell_size + app.wall_size) + app.margem_size, app.cell_size, app.cell_size, 0x00FF00, app.maze_pixel_width, app.maze_pixel_height)
                draw_maze_cell(app.data, app.size_line, cell, app.margem_size, app.wall_size, app.cell_size, 0x111827, app.maze_pixel_width, app.maze_pixel_height)
                draw_rect(app.data, app.size_line, app.exit_cell.x * (app.cell_size + app.wall_size) + app.margem_size, app.exit_cell.y * (app.cell_size + app.wall_size) + app.margem_size, app.cell_size, app.cell_size, 0xFF0000, app.maze_pixel_width, app.maze_pixel_height)

            app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)

        elif app.state == State.RESOLUTION_SHOWN:
            for cell in app.maze.visited_cells_resolution:
                draw_rect(app.data, app.size_line, app.entry_cell.x * (app.cell_size + app.wall_size) + app.margem_size, app.entry_cell.y * (app.cell_size + app.wall_size) + app.margem_size, app.cell_size, app.cell_size, 0x00FF00, app.maze_pixel_width, app.maze_pixel_height)
                draw_maze_cell(app.data, app.size_line, cell, app.margem_size, app.wall_size, app.cell_size, 0x00CFFF, app.maze_pixel_width, app.maze_pixel_height)
            draw_rect(app.data, app.size_line, app.exit_cell.x * (app.cell_size + app.wall_size) + app.margem_size, app.exit_cell.y * (app.cell_size + app.wall_size) + app.margem_size, app.cell_size, app.cell_size, 0xFF0000, app.maze_pixel_width, app.maze_pixel_height)

            app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)
            app.state = State.DONE
            return

    def key_options(keycode, param):

        print ("Keycode: ", keycode)
        if keycode == 65307:  # ESC
            app.ptr.mlx_loop_exit(app.mlx_ptr)
        if keycode == 114:  # R
            print("Resetting the maze...")
            app.maze = maze_generator(app.config)
            app.ptr.mlx_destroy_image(app.mlx_ptr, app.image)
            app.image = app.ptr.mlx_new_image(app.mlx_ptr, app.maze_pixel_width, app.maze_pixel_height)
            app.data, _, app.size_line, _ = app.ptr.mlx_get_data_addr(app.image)
            draw_rect(app.data, app.size_line, 0, 0, app.maze_pixel_width, app.maze_pixel_height, 0x000000, app.maze_pixel_width, app.maze_pixel_height)
            for cell in app.maze.pattern_cells:
                cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
                cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
                draw_rect(app.data, app.size_line, cx, cy, app.cell_size, app.cell_size, 0x0000FF, app.maze_pixel_width, app.maze_pixel_height)
            app.state = State.GENERATE
            app.generate_idx = 0
            app.resolution_idx = 0
        if keycode == 99:  # C
            print("Changing the color...")
            color1 = random.randint(0, 0xFFFFFF)
            color2 = random.randint(0, 0xFFFFFF)
            for cell in app.maze.visited_cells:
                cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
                cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
                draw_rect(app.data, app.size_line, cx, cy, app.cell_size, app.cell_size, color1, app.maze_pixel_width, app.maze_pixel_height)
                if not cell.north:
                    draw_rect(app.data, app.size_line, cx, cy - app.wall_size, app.cell_size, app.wall_size, color1, app.maze_pixel_width, app.maze_pixel_height)
                if not cell.south:
                    draw_rect(app.data, app.size_line, cx, cy + app.cell_size, app.cell_size, app.  wall_size, color1, app.maze_pixel_width, app.maze_pixel_height)
                if not cell.west:
                    draw_rect(app.data, app.size_line, cx - app.wall_size, cy, app.wall_size, app.cell_size, color1, app.maze_pixel_width, app.maze_pixel_height)
                if not cell.east:
                    draw_rect(app.data, app.size_line, cx + app.cell_size, cy, app.wall_size, app.cell_size, color1, app.maze_pixel_width, app.maze_pixel_height)
            for cell in app.maze.visited_cells_resolution:
                cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
                cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
                draw_rect(app.data, app.size_line, cx, cy, app.cell_size, app.cell_size, color2, app.maze_pixel_width, app.maze_pixel_height)
                if not cell.north:
                    draw_rect(app.data, app.size_line, cx, cy - app.wall_size, app.cell_size, app.wall_size, color2, app.maze_pixel_width, app.maze_pixel_height)
                if not cell.south:
                    draw_rect(app.data, app.size_line, cx, cy + app.cell_size, app.cell_size, app.wall_size, color2, app.maze_pixel_width, app.maze_pixel_height)
                if not cell.west:
                    draw_rect(app.data, app.size_line, cx - app.wall_size, cy, app.wall_size, app.cell_size, color2, app.maze_pixel_width, app.maze_pixel_height)
                if not cell.east:
                    draw_rect(app.data, app.size_line, cx + app.cell_size, cy, app.wall_size, app.cell_size, color2, app.maze_pixel_width, app.maze_pixel_height)
            app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)
        if keycode == 112:  # P
            print("Hide/Show resolution path...")
            if app.state == State.DONE:
                app.state = State.RESOLUTION_HIDDEN
            else:
                app.state = State.RESOLUTION_SHOWN
        if keycode == 115:  # S
            print("Solving the maze")
            if app.state == State.DONE:
                app.state = State.RESOLUTION
                app.resolution_idx = 0

    app.ptr.mlx_key_hook(app.win, key_options, None)
    def expose_hook(param):
        app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win, app.image, 0, 0)
    app.ptr.mlx_expose_hook(app.win, expose_hook, None)


    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 100, 0xAAAAAA, "Press R to reset the maze")
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 120, 0xAAAAAA, "Press C to change the color")
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 140, 0xAAAAAA, "Press P to hide/show resolution path")
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 160, 0xAAAAAA, "Press S to solve the maze")
    app.ptr.mlx_string_put(app.mlx_ptr, app.win, 900, 180, 0xAAAAAA, "Press ESC to quit")

    app.ptr.mlx_loop_hook(app.mlx_ptr, update, None)


    app.ptr.mlx_loop(app.mlx_ptr)

if __name__ == "__main__":
    main()