import time
import random
import mlx
import validate_config
import map

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

def main():

    ptr = mlx.Mlx()
    mlx_ptr = ptr.mlx_init()
    config = validate_config.read_config_file()
    maze = map.MazeGenerator(config)
    if maze.width * maze.height > 64:
        maze.pattern()
    else:
        print("The maze is too small to apply the pattern, skipping it...")
    maze.dfs(maze.maze[0])
    if not config.perfect:
        maze.not_perfect_maze()
    maze.reset_visited()
    maze.bfs_resolution(maze.get_cell(config.entry[0], config.entry[1]), maze.get_cell(config.exit[0], config.exit[1]))
    entry_cell = maze.get_cell(config.entry[0], config.entry[1])
    exit_cell = maze.get_cell(config.exit[0], config.exit[1])

    margem_size = 10
    wall_size = 5 if config.width > 39 else 10
    base_cell_size = max(config.width, config.height)
    cell_size = (900 - (2 * margem_size) - (base_cell_size + 1) * wall_size) // base_cell_size

    pixel_width_wall = (config.width + 1) * wall_size
    pixel_height_wall = (config.height + 1) * wall_size
    pixel_cells_width = config.width * cell_size
    pixel_cells_height = config.height * cell_size


    maze_pixel_width = pixel_width_wall + (2 * margem_size) + pixel_cells_width
    maze_pixel_height = pixel_height_wall + (2 * margem_size) + pixel_cells_height

    win = ptr.mlx_new_window(mlx_ptr, maze_pixel_width + 500, maze_pixel_height, "Maze Generator")

    state = "generate"
    generate_idx = 0
    resolution_idx = 0


    image = ptr.mlx_new_image(mlx_ptr, maze_pixel_width, maze_pixel_height)

    data, _, size_line, _ = ptr.mlx_get_data_addr(image)
    draw_rect(data, size_line, 0, 0, maze_pixel_width, maze_pixel_height, 0x000000, maze_pixel_width, maze_pixel_height)

    for cell in maze.pattern_cells:
        cx = margem_size + cell.x * (cell_size + wall_size)
        cy = margem_size + cell.y * (cell_size + wall_size)
        draw_rect(data, size_line, cx, cy, cell_size, cell_size, 0x0000FF, maze_pixel_width, maze_pixel_height)


    # for cell in maze.maze:
    #     cx = margem_size + cell.x * (cell_size + wall_size)
    #     cy = margem_size + cell.y * (cell_size + wall_size)
    #     draw_rect(data, size_line, cx, cy, cell_size, cell_size, 0x555555, maze_pixel_width, maze_pixel_height)
    #     if not cell.north:
    #         draw_rect(data, size_line, cx, cy - wall_size, cell_size, wall_size, 0x555555, maze_pixel_width, maze_pixel_height)
    #     if not cell.south:
    #         draw_rect(data, size_line, cx, cy + cell_size, cell_size, wall_size, 0x555555, maze_pixel_width, maze_pixel_height)
    #     if not cell.west:
    #         draw_rect(data, size_line, cx - wall_size, cy, wall_size, cell_size, 0x555555, maze_pixel_width, maze_pixel_height)
    #     if not cell.east:
    #         draw_rect(data, size_line, cx + cell_size, cy, wall_size, cell_size, 0x555555, maze_pixel_width, maze_pixel_height)
    #     ptr.mlx_expose_hook(win, expose_hook, None)


    map.output_maze(maze)


    def update(param):
        nonlocal generate_idx
        nonlocal resolution_idx
        nonlocal state

        if state == "generate":
            cell = maze.visited_cells[generate_idx]
            cx = margem_size + cell.x * (cell_size + wall_size)
            cy = margem_size + cell.y * (cell_size + wall_size)
            draw_rect(data, size_line, cx, cy, cell_size, cell_size, 0x555555, maze_pixel_width, maze_pixel_height)
            if not cell.north:
                draw_rect(data, size_line, cx, cy - wall_size, cell_size, wall_size, 0x555555, maze_pixel_width, maze_pixel_height)
            if not cell.south:
                draw_rect(data, size_line, cx, cy + cell_size, cell_size, wall_size, 0x555555, maze_pixel_width, maze_pixel_height)
            if not cell.west:
                draw_rect(data, size_line, cx - wall_size, cy, wall_size, cell_size, 0x555555, maze_pixel_width, maze_pixel_height)
            if not cell.east:
                draw_rect(data, size_line, cx + cell_size, cy, wall_size, cell_size, 0x555555, maze_pixel_width, maze_pixel_height)
            ptr.mlx_put_image_to_window(mlx_ptr, win, image, 0, 0)
            time.sleep(0.0001)
            generate_idx += 1

            if generate_idx >= len(maze.visited_cells):
                state = "resolution"
                return

        elif state == "resolution":
            draw_rect(data, size_line, entry_cell.x * (cell_size + wall_size) + margem_size, entry_cell.y * (cell_size + wall_size) + margem_size, cell_size, cell_size, 0x00FF00, maze_pixel_width, maze_pixel_height)
            draw_rect(data, size_line, exit_cell.x * (cell_size + wall_size) + margem_size, exit_cell.y * (cell_size + wall_size) + margem_size, cell_size, cell_size, 0xFF0000, maze_pixel_width, maze_pixel_height)
            cell = maze.visited_cells_resolution[resolution_idx]
            cell1 = maze.visited_cells_resolution[resolution_idx + 1] if resolution_idx + 1 < len(maze.visited_cells_resolution) else None
            cx = margem_size + cell.x * (cell_size + wall_size)
            cy = margem_size + cell.y * (cell_size + wall_size)
            draw_rect(data, size_line, cx, cy, cell_size, cell_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
            
            if cell.y > cell1.y:
                draw_rect(data, size_line, cx, cy - wall_size, cell_size, wall_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
            if cell.y < cell1.y:
                draw_rect(data, size_line, cx, cy + cell_size, cell_size, wall_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
            if cell.x > cell1.x:
                draw_rect(data, size_line, cx - wall_size, cy, wall_size, cell_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
            if cell.x < cell1.x:
                draw_rect(data, size_line, cx + cell_size, cy, wall_size, cell_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
            
            ptr.mlx_put_image_to_window(mlx_ptr, win, image, 0, 0)
            time.sleep(0.01)
            resolution_idx += 1
            if resolution_idx >= len(maze.visited_cells_resolution) - 1:
                state = "done"
                return
            
        elif state == "done":
            return
        
        elif state == "resolution_hidden":
            for cell in maze.visited_cells_resolution:
                draw_rect(data, size_line, entry_cell.x * (cell_size + wall_size) + margem_size, entry_cell.y * (cell_size + wall_size) + margem_size, cell_size, cell_size, 0x00FF00, maze_pixel_width, maze_pixel_height)
                cx = margem_size + cell.x * (cell_size + wall_size)
                cy = margem_size + cell.y * (cell_size + wall_size)
                draw_rect(data, size_line, cx, cy, cell_size, cell_size, 0x555555, maze_pixel_width, maze_pixel_height)
                if not cell.north:
                    draw_rect(data, size_line, cx, cy - wall_size, cell_size, wall_size, 0x555555, maze_pixel_width, maze_pixel_height)
                if not cell.south:
                    draw_rect(data, size_line, cx, cy + cell_size, cell_size, wall_size, 0x555555, maze_pixel_width, maze_pixel_height)
                if not cell.west:
                    draw_rect(data, size_line, cx - wall_size, cy, wall_size, cell_size, 0x555555, maze_pixel_width, maze_pixel_height)
                if not cell.east:
                    draw_rect(data, size_line, cx + cell_size, cy, wall_size, cell_size, 0x555555, maze_pixel_width, maze_pixel_height)
            draw_rect(data, size_line, exit_cell.x * (cell_size + wall_size) + margem_size, exit_cell.y * (cell_size + wall_size) + margem_size, cell_size, cell_size, 0xFF0000, maze_pixel_width, maze_pixel_height)
            ptr.mlx_put_image_to_window(mlx_ptr, win, image, 0, 0)

        elif state == "resolution_shown":
            for cell in maze.visited_cells_resolution:
                draw_rect(data, size_line, entry_cell.x * (cell_size + wall_size) + margem_size, entry_cell.y * (cell_size + wall_size) + margem_size, cell_size, cell_size, 0x00FF00, maze_pixel_width, maze_pixel_height)
                cx = margem_size + cell.x * (cell_size + wall_size)
                cy = margem_size + cell.y * (cell_size + wall_size)
                draw_rect(data, size_line, cx, cy, cell_size, cell_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
                if not cell.north:
                    draw_rect(data, size_line, cx, cy - wall_size, cell_size, wall_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
                if not cell.south:
                    draw_rect(data, size_line, cx, cy + cell_size, cell_size, wall_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
                if not cell.west:
                    draw_rect(data, size_line, cx - wall_size, cy, wall_size, cell_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
                if not cell.east:
                    draw_rect(data, size_line, cx + cell_size, cy, wall_size, cell_size, 0xAAAAAA, maze_pixel_width, maze_pixel_height)
            draw_rect(data, size_line, exit_cell.x * (cell_size + wall_size) + margem_size, exit_cell.y * (cell_size + wall_size) + margem_size, cell_size, cell_size, 0xFF0000, maze_pixel_width, maze_pixel_height)
            ptr.mlx_put_image_to_window(mlx_ptr, win, image, 0, 0)
            state = "done"
            return

    def key_options(keycode, param):
        nonlocal state
        nonlocal generate_idx
        nonlocal resolution_idx
        nonlocal image
        nonlocal maze
        nonlocal data
        nonlocal size_line

        print ("Keycode: ", keycode)
        if keycode == 65307:  # ESC
            ptr.mlx_loop_exit(mlx_ptr)
        if keycode == 114:  # R
            print("Resetting the maze...")
            maze = map.MazeGenerator(config)
            if maze.width * maze.height > 64:
                maze.pattern()
            else:
                print("The maze is too small to apply the pattern, skipping it...")
            maze.visited_cells = []
            maze.visited_cells_resolution = []
            maze.dfs(maze.maze[0])
            maze.reset_visited()
            maze.bfs_resolution(maze.get_cell(config.entry[0], config.entry[1]), maze.get_cell(config.exit[0], config.exit[1]))
            ptr.mlx_destroy_image(mlx_ptr, image)
            image = ptr.mlx_new_image(mlx_ptr, maze_pixel_width, maze_pixel_height)
            data, _, size_line, _ = ptr.mlx_get_data_addr(image)
            draw_rect(data, size_line, 0, 0, maze_pixel_width, maze_pixel_height, 0x000000, maze_pixel_width, maze_pixel_height)
            for cell in maze.pattern_cells:
                cx = margem_size + cell.x * (cell_size + wall_size)
                cy = margem_size + cell.y * (cell_size + wall_size)
                draw_rect(data, size_line, cx, cy, cell_size, cell_size, 0x0000FF, maze_pixel_width, maze_pixel_height)
            state = "generate"
            generate_idx = 0
            resolution_idx = 0
        if keycode == 99:  # C
            print("Changing the color...")
            color1 = random.randint(0, 0xFFFFFF)
            color2 = random.randint(0, 0xFFFFFF)
            for cell in maze.visited_cells:
                cx = margem_size + cell.x * (cell_size + wall_size)
                cy = margem_size + cell.y * (cell_size + wall_size)
                draw_rect(data, size_line, cx, cy, cell_size, cell_size, color1, maze_pixel_width, maze_pixel_height)
                if not cell.north:
                    draw_rect(data, size_line, cx, cy - wall_size, cell_size, wall_size, color1, maze_pixel_width, maze_pixel_height)
                if not cell.south:
                    draw_rect(data, size_line, cx, cy + cell_size, cell_size, wall_size, color1, maze_pixel_width, maze_pixel_height)
                if not cell.west:
                    draw_rect(data, size_line, cx - wall_size, cy, wall_size, cell_size, color1, maze_pixel_width, maze_pixel_height)
                if not cell.east:
                    draw_rect(data, size_line, cx + cell_size, cy, wall_size, cell_size, color1, maze_pixel_width, maze_pixel_height)
            for cell in maze.visited_cells_resolution:
                cx = margem_size + cell.x * (cell_size + wall_size)
                cy = margem_size + cell.y * (cell_size + wall_size)
                draw_rect(data, size_line, cx, cy, cell_size, cell_size, color2, maze_pixel_width, maze_pixel_height)
                if not cell.north:
                    draw_rect(data, size_line, cx, cy - wall_size, cell_size, wall_size, color2, maze_pixel_width, maze_pixel_height)
                if not cell.south:
                    draw_rect(data, size_line, cx, cy + cell_size, cell_size, wall_size, color2, maze_pixel_width, maze_pixel_height)
                if not cell.west:
                    draw_rect(data, size_line, cx - wall_size, cy, wall_size, cell_size, color2, maze_pixel_width, maze_pixel_height)
                if not cell.east:
                    draw_rect(data, size_line, cx + cell_size, cy, wall_size, cell_size, color2, maze_pixel_width, maze_pixel_height)
            ptr.mlx_put_image_to_window(mlx_ptr, win, image, 0, 0)
        if keycode == 112:  # P
            print("Hide/Show resolution path...")
            if state == "done":
                state = "resolution_hidden"
            else:
                state = "resolution_shown"

    ptr.mlx_key_hook(win, key_options, None)
    def expose_hook(param):
        ptr.mlx_put_image_to_window(mlx_ptr, win, image, 0, 0)
    ptr.mlx_expose_hook(win, expose_hook, None)


    ptr.mlx_string_put(mlx_ptr, win, 900, 100, 0xAAAAAA, "Press R to reset the maze")
    ptr.mlx_string_put(mlx_ptr, win, 900, 120, 0xAAAAAA, "Press C to change the color")
    ptr.mlx_string_put(mlx_ptr, win, 900, 140, 0xAAAAAA, "Press ESC to quit")
    ptr.mlx_string_put(mlx_ptr, win, 900, 160, 0xAAAAAA, "Press P to hide/show resolution \\n path")

    ptr.mlx_loop_hook(mlx_ptr, update, None)


    ptr.mlx_loop(mlx_ptr)

if __name__ == "__main__":
    main()