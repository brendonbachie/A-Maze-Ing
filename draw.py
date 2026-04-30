from map import Cell
from state import MazeState


def put_pixel(app: MazeState, x: int, y: int, color: int) -> None:
    """Coloca um pixel na imagem do labirinto.

    Calcula o offset na matriz de dados da imagem e atualiza os bytes
    correspondentes para definir a cor do pixel. Se as coordenadas
    estiverem fora do buffer, a função retorna sem alterações.

    Args:
        app: Estado da aplicação (inclui buffer de imagem e dimensões).
        x: Coordenada horizontal do pixel.
        y: Coordenada vertical do pixel.
        color: Cor no formato inteiro (hexadecimal).
    """
    offset = (y * app.size_line) + (x * 4)
    if offset < 0 or offset + 4 > len(app.data):
        return
    app.data[offset:offset+4] = (0xFF000000 | color).to_bytes(4, 'little')


def draw_rect(app: MazeState, x: int, y: int,
              width: int, height: int, color: int) -> None:
    """Desenha um retângulo na imagem do labirinto.

    Itera sobre os pixels dentro do retângulo e chama put_pixel para
    definir a cor de cada pixel, respeitando os limites do labirinto.

    Args:
        app: Estado da aplicação com informações de dimensão e buffer.
        x, y: Coordenadas do canto superior esquerdo do retângulo.
        width, height: Largura e altura do retângulo em pixels.
        color: Cor do retângulo.
    """
    for i in range(x, x + width):
        if i >= app.maze_pixel_width or i < 0:
            continue
        for j in range(y, y + height):
            if j >= app.maze_pixel_height or j < 0:
                continue
            put_pixel(app, i, j, color)


def draw_cell(app: MazeState, cell: Cell, color: int) -> None:
    """Desenha uma célula do labirinto na imagem.

    Calcula as coordenadas do canto superior esquerdo da célula com base
    nas dimensões da célula e na margem, e chama draw_rect para desenhá-la.

    Args:
        app: Estado da aplicação.
        cell: Célula a ser desenhada.
        color: Cor da célula.
    """

    cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
    cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
    draw_rect(app, cx, cy, app.cell_size, app.cell_size, color)


def draw_minotaur(app: MazeState, cell: Cell) -> None:
    """Desenha a imagem do Minotauro centralizada na célula indicada.

    Se a imagem do Minotauro não estiver carregada, a função retorna.
    Caso contrário, calcula a posição para centralizar a imagem e a
    desenha na janela do jogo.

    Args:
        app: Estado da aplicação com ponteiros de janela e imagens.
        cell: Célula onde o Minotauro deve ser desenhado.
    """
    if app.minotaur_image is None:
        return
    cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
    cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
    cx += (app.cell_size - app.minotaur_width) // 2
    cy += (app.cell_size - app.minotaur_height) // 2
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.minotaur_image, cx, cy)  # type: ignore


def draw_teseu(app: MazeState, cell: Cell) -> None:
    """Desenha a imagem de Teseu centralizada na célula indicada.

    Se a imagem de Teseu não estiver carregada, a função retorna.
    Caso contrário, calcula a posição para centralizar a imagem e a
    desenha na janela do jogo.

    Args:
        app: Estado da aplicação com ponteiros de janela e imagens.
        cell: Célula onde Teseu deve ser desenhado.
    """
    if app.teseu_image is None:
        return
    cx = app.margem_size + cell.x * (app.cell_size + app.wall_size)
    cy = app.margem_size + cell.y * (app.cell_size + app.wall_size)
    cx += (app.cell_size - app.teseu_width) // 2
    cy += (app.cell_size - app.teseu_height) // 2
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.teseu_image, cx, cy)  # type: ignore


def draw_teseu_victory(app: MazeState, cell: Cell) -> None:
    """Desenha a tela de vitória de Teseu na janela do jogo.

    Args:
        app: Estado da aplicação contendo a imagem de vitória.
        cell: Parâmetro não utilizado, mantido para compatibilidade.
    """
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.teseu_victory, 0, 0)  # type: ignore


def draw_minotaur_victory(app: MazeState, cell: Cell) -> None:
    """Desenha a tela de vitória do Minotauro na janela do jogo.

    Args:
        app: Estado da aplicação contendo a imagem de vitória.
        cell: Parâmetro não utilizado, mantido para compatibilidade.
    """
    app.ptr.mlx_put_image_to_window(app.mlx_ptr, app.win,
                                    app.minotaur_victory, 0, 0)  # type: ignore


def draw_connection(app: MazeState, cell1: Cell,
                    cell2: Cell, color: int) -> None:
    """Desenha a conexão entre duas células adjacentes.

    Calcula as coordenadas do canto superior esquerdo da primeira célula e,
    com base nas posições relativas das duas células, desenha um retângulo
    que representa a passagem entre elas.

    Args:
        app: Estado da aplicação.
        cell1, cell2: Células adjacentes que serão conectadas.
        color: Cor da conexão.
    """
    cx1 = app.margem_size + cell1.x * (app.cell_size + app.wall_size)
    cy1 = app.margem_size + cell1.y * (app.cell_size + app.wall_size)

    if cell1.y > cell2.y:
        draw_rect(app, cx1, cy1 - app.wall_size, app.cell_size,
                  app.wall_size, color)

    if cell1.y < cell2.y:
        draw_rect(app, cx1, cy1 + app.cell_size, app.cell_size,
                  app.wall_size, color)

    if cell1.x > cell2.x:
        draw_rect(app, cx1 - app.wall_size, cy1, app.wall_size,
                  app.cell_size, color)

    if cell1.x < cell2.x:
        draw_rect(app, cx1 + app.cell_size, cy1, app.wall_size,
                  app.cell_size, color)


def draw_maze_cell(app: MazeState, cell: Cell, color: int) -> None:
    """Desenha uma célula do labirinto, incluindo suas paredes.

    Desenha a célula principal e, dependendo do estado das paredes,
    desenha retângulos para representar aberturas (paredes removidas).

    Args:
        app: Estado da aplicação.
        cell: Célula a ser desenhada.
        color: Cor da célula.
    """
    cx = app.wall_size + cell.x * (app.cell_size + app.wall_size)
    cy = app.wall_size + cell.y * (app.cell_size + app.wall_size)

    draw_cell(app, cell, color)

    if not cell.north:
        draw_rect(app, cx, cy - app.wall_size, app.cell_size,
                  app.wall_size, color)
    if not cell.west:
        draw_rect(app, cx - app.wall_size, cy, app.wall_size,
                  app.cell_size, color)

    if not cell.south:
        draw_rect(app, cx, cy + app.cell_size, app.cell_size,
                  app.wall_size, color)

    if not cell.east:
        draw_rect(app, cx + app.cell_size, cy, app.wall_size,
                  app.cell_size, color)


def draw_entry_exit(app: MazeState) -> None:
    """Desenha as células de entrada e saída do labirinto.

    Desenha a célula de entrada em verde e a de saída em vermelho.

    Args:
        app: Estado da aplicação contendo referências às células de entry/exit.
    """
    draw_cell(app, app.entry_cell, 0x00FF00)
    draw_cell(app, app.exit_cell, 0xFF0000)


def draw_resolution_path(app: MazeState, color: int) -> None:
    """Desenha o caminho de resolução do labirinto.

    Itera sobre as células visitadas durante a resolução e desenha cada
    célula e a conexão até a próxima. Atualiza também as células de
    entrada/saída e força a atualização da janela.

    Args:
        app: Estado da aplicação com o labirinto já resolvido.
        color: Cor usada para desenhar o caminho.
    """
    for cell, cell1 in zip(app.maze.visited_cells_resolution,
                           app.maze.visited_cells_resolution[1:]):
        draw_cell(app, cell, color)
        draw_connection(app, cell, cell1, color)
    draw_entry_exit(app)
    app.expose_hook(None)


def draw_resolution_path_game(app: MazeState, color: int) -> None:
    """Desenha o caminho de resolução do labirinto durante o jogo.

    Itera sobre as células visitadas pela rotina de resolução do labirinto
    associada à instância de jogo (crete_maze) e desenha o caminho, a célula
    de saída e força a atualização da janela.

    Args:
        app: Estado da aplicação do jogo.
        color: Cor usada para desenhar o caminho.
    """

    for cell, cell1 in zip(app.crete_maze.maze.visited_cells_resolution,
                           app.crete_maze.maze.visited_cells_resolution[1:]):
        draw_cell(app, cell, color)
        draw_connection(app, cell, cell1, color)
    draw_cell(app, app.exit_cell, 0xFF0000)
    app.expose_hook(None)


def draw_full_maze(app: MazeState, color: int) -> None:
    """Desenha o labirinto completo exibindo todas as células geradas.

    Itera sobre as células visitadas durante a geração do labirinto e desenha
    cada uma usando draw_maze_cell. Em seguida desenha entrada/saída e
    atualiza a janela.

    Args:
        app: Estado da aplicação contendo o labirinto gerado.
        color: Cor usada para desenhar as células.
    """
    for cell in app.maze.visited_cells:
        draw_maze_cell(app, cell, color)

    draw_entry_exit(app)
    app.expose_hook(None)


def draw_full_maze_game(app: MazeState, color: int) -> None:
    """Desenha o labirinto completo durante o jogo, incluindo agentes.

    Desenha as células geradas, a célula de saída e, dependendo do estado,
    a célula de Teseu. Atualiza a janela e desenha o sprite de Teseu.

    Args:
        app: Estado da aplicação do jogo.
        color: Cor usada para desenhar as células.
    """
    for cell in app.crete_maze.maze.visited_cells:
        draw_maze_cell(app, cell, color)
    draw_cell(app, app.exit_cell, 0xFF0000)
    if app.state != app.state.PLAYER_MOVE:
        draw_cell(app, app.teseu_cell, 0x00FF00)
    app.expose_hook(None)
    draw_teseu(app, app.teseu_cell)


def loop_idle(_: None) -> None:
    """Mantém o loop de eventos do jogo ativo sem fazer nada.

    Função utilizada como callback para quando o loop não tem
    eventos a processar.
    """
    pass
