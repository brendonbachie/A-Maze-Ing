import mlx
import validate_config
import map

#função pra aumentar pixel
def big_pixel(ptr, mlx_ptr, win, x, y, color, size):
    for i in range(size):
        for j in range(size):
            ptr.mlx_pixel_put(mlx_ptr, win, (x * size + 10) + i, (y * size + 10) + j, color)


def main():
    config = validate_config.read_config_file()
    maze = map.MazeGenerator(config)

    #inicia ponteiro 
    ptr = mlx.Mlx()
    mlx_ptr = ptr.mlx_init()

    #inicia janela
    win = ptr.mlx_new_window(mlx_ptr, 800, 600, "Maze Generator")

    #função pra fechar janela com esc
    def close_window(keycode, param):
        print(f"Tecla pressionada: {keycode}")
        if keycode == 65307:
            ptr.mlx_destroy_window(mlx_ptr, win)
            ptr.mlx_loop_exit(mlx_ptr)
    ptr.mlx_key_hook(win, close_window, None)

    #loop pra chamar celula por celula pra printar)
    for cell in maze.maze:
        print(f"Cell: ({cell.x}, {cell.y}), North: {cell.north}, South: {cell.south}, East: {cell.east}, West: {cell.west}")
        big_pixel(ptr, mlx_ptr, win, cell.x, cell.y, 0xFFFFFF, 10)
    ptr.mlx_loop(mlx_ptr)

if __name__ == "__main__":
    main()