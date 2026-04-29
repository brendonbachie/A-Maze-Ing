"""Estado da aplicação e utilitários para renderização do labirinto.

Define o enum State e a classe MazeState que inicializa o labirinto,
recupera configurações e provê funções auxiliares para calcular dimensões
para renderização.
"""

import validate_config
import game
from validate_config import Configuration as cfg
from map import Cell, MazeGenerator
from enum import Enum
import mlx  # type: ignore


class State(Enum):
    GENERATE = 1
    RESOLUTION = 2
    DONE = 3
    RESOLUTION_HIDDEN = 4
    RESOLUTION_SHOWN = 5
    NOT_RESOLUTION = 6
    TESEU = 7
    MINOTAUR = 8
    GAME = 9
    PLAYER_MOVE = 10
    END_GAME = 11


class MazeState():
    """Mantém o estado global da aplicação e recursos gráficos.

    A instância carrega a configuração, gera o labirinto e, quando em modo
    de jogo, inicializa o estado do jogo (GameState). Também guarda recursos
    gráficos, cores, índices de animação e buffers.
    """

    def __init__(self) -> None:
        """Inicializa o estado do aplicativo lendo a configuração e gerando o labirinto.

        O construtor cria instâncias necessárias, gera o labirinto e prepara
        recursos iniciais para renderização e jogo.
        """
        self.config: cfg = validate_config.read_config_file()
        self.maze: MazeGenerator = MazeGenerator(self.config)
        self.maze.generate(True)
        if self.config.gamemode:
            self.crete_maze: game.GameState = (
                game.GameState.generate_game_state(self.config))
        self.entry_cell: Cell = Cell(-1, -1)
        self.exit_cell: Cell = Cell(-1, -1)
        self.teseu_cell: Cell = Cell(-1, -1)
        self.minotaur_cell: Cell = Cell(-1, -1)
        self.margem_size: int = 0
        self.wall_size: int = 0
        self.cell_size: int = 0
        self.maze_pixel_width: int = 0
        self.maze_pixel_height: int = 0
        self.ptr: mlx.Mlx = mlx.Mlx()  # type: ignore
        self.mlx_ptr: mlx.Mlx = self.ptr.mlx_init()  # type: ignore
        self.win: mlx.Mlx | None = None
        self.state = State.DONE
        self.last_state = State.NOT_RESOLUTION
        self.generate_idx = 0
        self.resolution_idx = 0
        self.resolution_idx_t = 0
        self.resolution_idx_m = 0
        self.image: mlx.Mlx | None = None
        self.is_generate: bool = False
        self.data: bytearray = bytearray()
        self.size_line: int = 0
        self.path_color = 0x00CFFF
        self.maze_color = 0x111827
        self.pattern_color = 0x3B82F6
        self.background_color = 0x374151
        self.minotaur_image: mlx.Mlx | None = None
        self.minotaur_width: int = 0
        self.minotaur_height: int = 0
        self.teseu_image: mlx.Mlx | None = None
        self.teseu_width: int = 0
        self.teseu_height: int = 0
        self.teseu_victory: mlx.Mlx | None = None
        self.teseu_victory_width: int = 0
        self.teseu_victory_height: int = 0
        self.minotaur_victory: mlx.Mlx | None = None
        self.minotaur_victory_width: int = 0
        self.minotaur_victory_height: int = 0
        self.ariadne: bool = False

    def initialize_mlx(self) -> None:
        """Inicializa a janela e os recursos gráficos necessários para renderizar o labirinto.

        Calcula as dimensões de estrutura, cria a imagem e obtém o buffer
        de dados para desenho.
        """

        self.margem_size, self.wall_size, self.cell_size = (
            structure_dimensions(self.config))

        self.maze_pixel_width, self.maze_pixel_height = total_pixel_dimensions(
            self.config, self)

        self.image = self.ptr.mlx_new_image(
            self.mlx_ptr, self.maze_pixel_width,
            self.maze_pixel_height)  # type: ignore

        self.data, _, self.size_line, _ = self.ptr.mlx_get_data_addr(
            self.image)  # type: ignore

    def expose_hook(self, _: None) -> None:
        """Redesenha a imagem atual na janela do aplicativo.

        Usa o ponteiro para colocar a imagem (buffer) na janela.
        """
        self.ptr.mlx_put_image_to_window(self.mlx_ptr,
                                         self.win, self.image,
                                         0, 0)  # type: ignore


def structure_dimensions(config: cfg) -> tuple[int, int, int]:
    """Calcula as dimensões internas (margem, parede, célula) para renderização.

    Retorna uma tupla com (margem_size, wall_size, cell_size) baseada nos
    parâmetros de configuração do labirinto.
    """
    wall_size = 2 if config.width > 50 else 4
    margem_size = wall_size
    base_cell_size = max(config.width, config.height)
    cell_size = (900 - (2 * margem_size) - (
        base_cell_size + 1) * wall_size) // base_cell_size
    return margem_size, wall_size, cell_size


def total_pixel_dimensions(config: cfg, mlx: MazeState) -> tuple[int, int]:
    """Calcula as dimensões totais em pixels necessárias para renderizar o labirinto.

    Retorna (maze_pixel_width, maze_pixel_height) considerando paredes,
    margens e células.
    """
    pixel_width_wall = (config.width + 1) * mlx.wall_size
    pixel_height_wall = (config.height + 1) * mlx.wall_size
    pixel_cells_width = config.width * mlx.cell_size
    pixel_cells_height = config.height * mlx.cell_size
    maze_pixel_width = (
        pixel_width_wall + (2 * mlx.margem_size) + pixel_cells_width)
    maze_pixel_height = pixel_height_wall + (
        2 * mlx.margem_size) + pixel_cells_height

    return maze_pixel_width, maze_pixel_height
