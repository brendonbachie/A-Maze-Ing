from validate_config import Configuration
from map import Cell, MazeGenerator


class GameState:
    """Representa o estado do jogo, incluindo labirinto, agentes e caminhos.

    A instância contém o labirinto gerado, posições de Teseu, Minotauro e
    da saída, listas com os caminhos calculados, contadores de movimentos
    e flags que indicam o término e o vencedor do jogo.
    """

    def __init__(self, config: Configuration):
        """Inicializa o estado do jogo a partir de uma configuração.

        Define o labirinto a partir da configuração, inicializa as posições
        de Teseu e do Minotauro com valores sentinela, conta de movimentos,
        caminhos e flags de jogo.

        Args:
            config: Objeto Configuration com os parâmetros do labirinto.
        """
        self.config = config
        self.maze: MazeGenerator = MazeGenerator(self.config)
        self.maze.generate(False)
        self.teseu_pos: Cell = Cell(-1, -1)
        self.minotaur_pos: Cell = Cell(-1, -1)
        self.exit_pos: Cell = Cell(-1, -1)
        self.teseu_moves = 20
        self.minotaur_moves = 10
        self.teseu_idx = 0
        self.minotaur_idx = 0
        self.teseu_path: list[Cell] = []
        self.minotaur_path: list[Cell] = []
        self.game_over = False
        self.teseu_wins = False

    @staticmethod
    def generate_game_state(configs: Configuration) -> "GameState":
        """Cria e retorna o estado inicial do jogo a partir da configuração.

        Gera o labirinto, posiciona Teseu, Minotauro e a saída, e calcula os
        caminhos iniciais (BFS) para Teseu e Minotauro.

        Args:
            configs: Objeto Configuration com os valores de
            configuração do labirinto.

        Returns:
            Uma instância de GameState com o estado inicial do jogo.
        """
        crete = GameState(configs)
        crete.teseu_pos = crete.maze.teseu
        crete.minotaur_pos = crete.maze.minotaur
        crete.exit_pos = crete.maze.get_cell(configs.exit[0], configs.exit[1])
        crete.teseu_path = crete.maze.bfs_game(crete.teseu_pos,
                                               crete.minotaur_pos)
        crete.minotaur_path = crete.maze.bfs_game(crete.minotaur_pos,
                                                  crete.exit_pos
                                                  )
        return crete
