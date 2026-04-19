import mlx

ptr = mlx.Mlx()

# inicia mlx
mlx_ptr = ptr.mlx_init()

# cria janela
win = ptr.mlx_new_window(mlx_ptr, 800, 600, "Teste Image Buffer")

# cria imagem em memória
img = ptr.mlx_new_image(mlx_ptr, 800, 600)

# pega acesso bruto aos pixels da imagem
addr = ptr.mlx_get_data_addr(img)


def draw_pixels(param):
    # exemplo: desenhar um quadrado branco de 100x100
    #
    # aqui estamos usando pixel_put ainda só como fallback visual,
    # porque alguns wrappers python variam no acesso ao buffer bruto.
    #
    # depois vamos ajustar diretamente no addr se necessário.

    for x in range(200, 300):
        for y in range(200, 300):
            ptr.mlx_pixel_put(mlx_ptr, win, x, y, 0x00FF00)

    # envia imagem para a janela
    ptr.mlx_put_image_to_window(mlx_ptr, win, img, 0, 0)


def close_window(keycode, param):
    if keycode == 65307:  # ESC
        ptr.mlx_destroy_window(mlx_ptr, win)
        ptr.mlx_loop_exit(mlx_ptr)

addr = ptr.mlx_get_data_addr(img)
print(type(addr))
print(addr)

ptr.mlx_expose_hook(win, draw_pixels, None)
ptr.mlx_key_hook(win, close_window, None)

ptr.mlx_loop(mlx_ptr)