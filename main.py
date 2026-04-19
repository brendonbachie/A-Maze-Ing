import mlx
import validate_config
import map

''' Agradecer a MiniLibX por ser extremamente zoada e não deixar eu simplesmente printar pixels na tela com o mlx.pixel_put, 
tive que criar uma imagem em memória, pegar o acesso bruto aos pixels, e depois enviar a imagem para a janela.

VAI TOMAR NO CU, MLX
'''
#Função pra colocar um pixel na imagem, calculando o offset correto baseado no x, y, e tamanho da linha
def put_pixel(data, size_line, x, y, color):
    offset = (y * size_line) + (x * 4)
    data[offset:offset+4] = (0xFF000000 | color).to_bytes(4, 'little')

#Função pra desenhar as paradas na tela baseado na posição x, y, largura, altura, e cor
def draw_rect(data, size_line, x, y, width, height, color, total_pixel_width, total_pixel_height):
    for i in range(x, x + width):
        if i >= total_pixel_width or i < 0:
            continue
        for j in range(y, y + height):
            if j >= total_pixel_height or j < 0:
                continue
            put_pixel(data, size_line, i, j, color)


def main():
    #Variaveis de tamanhos da parede e da celula

    #iniciando o demonio da mlx, depois pego as configurações do arquivo e a classe que gera o labirinto
    ptr = mlx.Mlx()
    mlx_ptr = ptr.mlx_init()
    config = validate_config.read_config_file()
    maze = map.MazeGenerator(config)

    wall_size = int(cell_size // 5)
    cell_size = (800 - (config.width + 1) * wall_size - 2 * margem_size) // config.width
    margem_size = 10

    pixel_width_wall = (config.width + 1) * wall_size
    pixel_height_wall = (config.height + 1) * wall_size

    maze_pixel_width = (config.width * cell_size) +((config.width + 1) * wall_size)
    maze_pixel_height = (config.height * cell_size) + ((config.height + 1) * wall_size)

    total_pixel_width = (config.width * cell_size) + pixel_width_wall + (2 * margem_size)
    total_pixel_height = (config.height * cell_size) + pixel_height_wall + (2 * margem_size)

    offset_x = (800 - maze_pixel_width) // 2
    offset_y = (800 - maze_pixel_height) // 2

    #Criando a janela com o tamanho calculado
    win = ptr.mlx_new_window(mlx_ptr, 800, 800, "Maze Generator")

    #Função macia pra fechar a janela quando aperta ESC
    def close_window(keycode, param):
        if keycode == 65307:  # ESC
            ptr.mlx_destroy_window(mlx_ptr, win)
            ptr.mlx_loop_exit(mlx_ptr)

    #Criando a imagem em memória com o tamanho total calculado
    image = ptr.mlx_new_image(mlx_ptr, 800, 800)

    #Pegando o acesso bruto aos pixels da imagem, e as informações de bytes por pixel, tamanho da linha, e endianess
    data, bpp, size_line, endian = ptr.mlx_get_data_addr(image)

    draw_rect(data, size_line, 0, 0, 800, 800, 0xFF00FF, 800, 800)
    #Loop da mlx, onde a magia acontece
    for cell in maze.maze:
        cx = offset_x + cell.x * (cell_size + wall_size)
        cy = offset_y + cell.y * (cell_size + wall_size)
        draw_rect(data, size_line, cx, cy, cell_size, cell_size, 0xFF00FF, 800, 800)
        if cell.north:
            draw_rect(data, size_line, cx, cy - wall_size, cell_size + wall_size, wall_size, 0x000000, 800, 800)
        if cell.south:
            draw_rect(data, size_line, cx, cy + cell_size, cell_size + wall_size, wall_size, 0x000000, 800, 800)
        if cell.west:
            draw_rect(data, size_line, cx - wall_size, cy, wall_size, cell_size + wall_size, 0x000000, 800, 800)
        if cell.east:
            draw_rect(data, size_line, cx + cell_size, cy, wall_size, cell_size + wall_size, 0x000000, 800, 800)


    def expose_hook(param):
        ptr.mlx_put_image_to_window(mlx_ptr, win, image, 0, 0)
    
    ptr.mlx_expose_hook(win, expose_hook, None)
    ptr.mlx_key_hook(win, close_window, None)
    ptr.mlx_loop(mlx_ptr)

if __name__ == "__main__":
    main()