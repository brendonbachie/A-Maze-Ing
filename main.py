import time

import mlx
import validate_config
import map

''' Agradecer a MiniLibX por ser extremamente zoada e não deixar eu simplesmente printar pixels na tela com o mlx.pixel_put, 
tive que criar uma imagem em memória, pegar o acesso bruto aos pixels, e depois enviar a imagem para a janela.

VAI TOMAR NO CU, MLX
'''
'''========================================================================================================================================================================================================'''

'''Função pra colocar um pixel na imagem, calculando o offset correto baseado no x, y, e tamanho da linha.
A função recebe o data (que é o array de bytes que representa os pixels da imagem), o tamanho da linha (que é a quantidade de bytes que cada linha de pixels ocupa),
a posição x e y do pixel, e a cor do pixel (que é um inteiro representando a cor em formato ARGB).
offset é o número de bytes que a posição do pixel ocupa na imagem, calculado multiplicando a posição y pelo tamanho da linha (pra pular as linhas anteriores),
e somando a posição x multiplicada por 4 (porque cada pixel ocupa 4 bytes, um pra cada canal de cor).
Depois, a função coloca a cor do pixel no data, usando bitwise OR pra garantir que o canal alpha seja sempre 255 (0xFF000000), e convertendo a cor para bytes usando to_bytes, com 4 bytes e little endian.
Precisei fazer uma verificação no offset, pra caso der ruim, ele não dar comportamento indefinido'''

'''Pra ser bem sincero, eu pouco sei sobre essa questão do endianess, mas como eu tô usando little endian, caguei e coloquei little mesmo, e aparentemente tá funcionando, então tá de boa.
Não entendi muito bem a questão do endianess, nem como essa função funciona em si. Infelizmente foi completamente vibecodada, mas pelo menos tá funcionando, então tá de boa.
90%, Rafael Ferro. Tá aqui seus 10% de vibecoding, aproveite.'''
def put_pixel(data, size_line, x, y, color):
    offset = (y * size_line) + (x * 4)
    if offset < 0 or offset + 4 > len(data):
        return
    data[offset:offset+4] = (0xFF000000 | color).to_bytes(4, 'little')

'''Função pra desenhar as paradas na tela baseado na posição x, y, largura, altura, e cor
    Pra essa função, eu passo o data e o size_line, tamanho, posição, cor... Essa porra pega a merda toda de tudo.
    Se eu usar só a merda do put_pixel, vai aparecer só um pixel, então eu imprimo tipo uma matriz de pixels, 
    onde i vai ser a posição x e o final da largura, e j vai ser a posição y e o final da altura, e pra cada pixel nessa matriz eu chamo a função put_pixel pra colocar a cor correta.
    A função também tem que verificar se os pixels estão dentro dos limites da imagem, pra não estourar o array.'''
def draw_rect(data, size_line, x, y, width, height, color, total_pixel_width, total_pixel_height):
    for i in range(x, x + width):
        if i >= total_pixel_width or i < 0:
            continue
        for j in range(y, y + height):
            if j >= total_pixel_height or j < 0:
                continue
            put_pixel(data, size_line, i, j, color)


def main():

    '''iniciando o demonio da mlx, depois pego as configurações do arquivo e a classe que gera o labirinto'''
    ptr = mlx.Mlx()
    mlx_ptr = ptr.mlx_init()
    config = validate_config.read_config_file()
    maze = map.MazeGenerator(config)
    maze.dfs(maze.maze[0])
    maze.dfs_resolution(maze.get_cell(config.entry[0], config.entry[1]), maze.get_cell(config.exit[0], config.exit[1]))

    margem_size = 10
    wall_size = 4 if config.width < 50 else 1
    base_cell_size = max(config.width, config.height)
    cell_size = (900 - (2 * margem_size) - (base_cell_size + 1) * wall_size) // base_cell_size

    pixel_width_wall = (config.width + 1) * wall_size
    pixel_height_wall = (config.height + 1) * wall_size
    pixel_cells_width = config.width * cell_size
    pixel_cells_height = config.height * cell_size

    maze_pixel_width = pixel_width_wall + (2 * margem_size) + pixel_cells_width
    maze_pixel_height = pixel_height_wall + (2 * margem_size) + pixel_cells_height

    win = ptr.mlx_new_window(mlx_ptr, maze_pixel_width, maze_pixel_height, "Maze Generator")

    def close_window(keycode, param):
        if keycode == 65307:  # ESC
            ptr.mlx_loop_exit(mlx_ptr)

    image = ptr.mlx_new_image(mlx_ptr, maze_pixel_width, maze_pixel_height)

    data, _, size_line, _ = ptr.mlx_get_data_addr(image)
   
    draw_rect(data, size_line, 0, 0, maze_pixel_width, maze_pixel_height, 0x000000, maze_pixel_width, maze_pixel_height)
    


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

    
    '''Depois de todo o trabalho, a merda da imagem ainda não aparece, porque nada pode ser tão fácil.
    Tive que criar uma função de expose, que vai ser chamada toda vez que a janela precisar ser redesenhada, 
    e essa função vai chamar a função mlx_put_image_to_window pra colocar a imagem na janela, e depois chamar 
    a função mlx_expose_hook pra registrar essa função de expose como o callback de expose da janela, pra que ela seja chamada toda vez que a janela precisar ser redesenhada.
    
    Essa porra de hook é confuso pra crl. Tem que criar uma função pra poder usar nela, aí coloca um param inútil nela, 
    e depois chama a função mlx_expose_hook passando o ponteiro da janela, a função de expose, e um parâmetro opcional (que não vou usar).
    Irmão, ZERO necessidade dessa volta toda. Por que só não posso chamar a função mlx_put_image_to_window direto aqui?

    Eu tô basicamente usando 3 funções numa porra que poderia ser feita com 1 função,
    e ainda ter que criar uma função de expose só pra isso, onde só a porra de um While(True) já resolveria (copilot, o while(True) resolveria?

    Copilot: "Sim, um while(True) poderia resolver, mas não seria a melhor solução, porque ele iria consumir 100% da CPU, enquanto a função de expose 
    só seria chamada quando a janela precisasse ser redesenhada, economizando recursos do sistema.")
    
    Vai tomar no cu tu e a MLX, copilot'''

    '''Mesmo problema do hook lá do expose, mas aqui é pra chamar a função de fechar a janela quando aperta ESC, que eu já expliquei lá em cima.'''
    ptr.mlx_key_hook(win, close_window, None)



    '''Essa função update vai fazer conseguir printar célula por célula. No momento ela só está printando a malha inteira, porque o DFS ainda não está
    implementado, mas a ideia é que ela vá printando as células conforme o DFS vai visitando elas, pra dar um efeito visual de construção do labirinto.
    Ela é basicamente o loop macio lá de cima, mas tem um indice que vai visitar todas as células da malha. Pra cada célula, ela faz o mesmo processo 
    de calcular a posição dos pixels do loop, a diferença aqui é que ela faz apenas de um, deixando o loop a cargo do loop_hook (mains um while(true) da vida)
    no final, ela usa um time.sleep pra segurar o loop por 0.05s e dar o efeito de frame por frame (usar timestap talvez?) e depois incrementa index pro próximo frame.'''
    len_maze = len(maze.maze)
    state = "generate"
    generate_idx = 0
    resolution_idx = 0
    
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
            cell = maze.visited_cells_resolution[resolution_idx]
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
            ptr.mlx_put_image_to_window(mlx_ptr, win, image, 0, 0)
            time.sleep(0.01)
            resolution_idx += 1
            if resolution_idx >= len(maze.visited_cells_resolution):
                state = "done"
                return
        elif state == "done":
            return

    def expose_hook(param):
        ptr.mlx_put_image_to_window(mlx_ptr, win, image, 0, 0)
    '''Esse primeiro expose_hook é necessário pra mostrar a imagem inicial (que é só o fundo) na janela, e depois o loop_hook vai ficar chamando a função update '''
    ptr.mlx_expose_hook(win, expose_hook, None)

    '''O loop_hook é uma função da mlx que recebe um ponteiro da mlx, uma função de callback, e um parâmetro opcional (que não vou usar), e fica chamando a função de callback em um loop, passando 
    o parâmetro opcional pra ela, até que a função de callback retorne False ou a janela seja fechada.'''
    ptr.mlx_loop_hook(mlx_ptr, update, None)

    '''Finalmente, depois de toda essa merda, a função mlx_loop é chamada pra iniciar o loop da mlx, que vai ficar rodando até a janela ser fechada, e
    vai chamar os callbacks registrados (expose_hook e close_window) quando necessário.'''
    ptr.mlx_loop(mlx_ptr)

if __name__ == "__main__":
    main()