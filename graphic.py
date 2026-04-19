import mlx

ptr = mlx.Mlx()

mlx_ptr = ptr.mlx_init()

win = ptr.mlx_new_window(mlx_ptr, 800, 600, "Hello World")

def close_window(keycode):
    print(f"Tecla pressionada: {keycode}")
    if keycode == 65307:
        ptr.mlx_destroy_window(mlx_ptr, win)
        ptr.mlx_loop_exit(mlx_ptr)


ptr.mlx_key_hook(win, close_window, None)

ptr.mlx_loop(mlx_ptr)