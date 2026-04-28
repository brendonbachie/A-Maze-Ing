from validate_config import Configuration
from map import Cell, MazeGenerator


class GameState:
    def __init__(self, config: Configuration):
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

# criar o labirinto com teseu de entrada e minotaur como saída
    @staticmethod
    def generate_game_state(configs: Configuration) -> "GameState":
        crete = GameState(configs)
        # coloca o teseu na posição de entrada do labirinto
        crete.teseu_pos = crete.maze.teseu
        # coloca o minotaur em uma posição aleatória do labirinto
        crete.minotaur_pos = crete.maze.minotaur
        # coloca a saída do labirinto
        crete.exit_pos = crete.maze.get_cell(configs.exit[0], configs.exit[1])
        crete.teseu_path = crete.maze.bfs_game(crete.teseu_pos,
                                               crete.minotaur_pos)
        crete.minotaur_path = crete.maze.bfs_game(crete.minotaur_pos,
                                                  crete.exit_pos
                                                  )
        return crete

