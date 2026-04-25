from validate_config import Configuration
from map import Cell, MazeGenerator, game_maze_generator


class GameState:
    def __init__(self, config: Configuration):
        self.config = config
        self.maze: MazeGenerator = None
        self.teseu_pos = self.config.teseu
        self.minotaur_pos = self.config.minotaur
        self.exit_pos = self.config.exit
        self.teseu_moves = 20
        self.minotaur_moves = 10
        self.teseu_idx = 0
        self.minotaur_idx = 0
        self.teseu_path: list[Cell] = []
        self.minotaur_path: list[Cell] = []
        self.game_over = False
        self.teseu_wins = False


# criar o labirinto com teseu de entrada e minotaur como saída
def generate_game_state(configs: Configuration) -> GameState:
    crete = GameState(configs)
    crete.maze = game_maze_generator(configs)
    # coloca o teseu na posição de entrada do labirinto
    crete.teseu_pos = crete.maze.get_cell(configs.teseu[0], configs.teseu[1])
    # coloca o minotaur em uma posição aleatória do labirinto
    crete.minotaur_pos = crete.maze.get_cell(configs.minotaur[0],
                                             configs.minotaur[1]
                                             )
    # coloca a saída do labirinto
    crete.exit_pos = crete.maze.get_cell(configs.exit[0], configs.exit[1])
    crete.teseu_path = crete.maze.bfs_game(crete.teseu_pos, crete.minotaur_pos)
    # for i, cell in enumerate(teseu_path):
    #     if i <= 20:
    #         crete.teseu_path.append(cell)
    crete.minotaur_path = crete.maze.bfs_game(crete.minotaur_pos,
                                              crete.exit_pos
                                              )
    # for i, cell in enumerate(minotaur_path):
    #     if i <= 10:
    #         crete.minotaur_path.append(cell)
    return crete


'''Enquanto o caminho (index) < 20, se ele for % 2 == 0, move o minotaur e\
teseu, se for % 2 == 1, move só o teseu.
diminui o número de movimentos do minotaur e do teseu, e verifica se o teseu \
chegou no minotaur.
Se não chegou, pega a posição de teseu, config.entry = posição de teseu, \
config.exit = posição do minotaur,
gera um mapa novo, adiciona movimentos do minotaur e do teseu, e continua o \
loop. Se chegou, teseu ganha,
e aí ele busca a saída do labirinto'''


'''Aqui vai ficar a questão do jogo, o teseu e o minotaur, a mudança de \
labirinto e as regras

A principio, Teseu tera 20 movimentos no labirinto e minotaur 10. Pela \
mitologia original,
Teseu matou o minotaur e saiu do labirinto. Então temos basicamente:
- Teseu tem 20 movimentos
- Minotaur tem 10 movimentos
- Se Teseu não chegar no Minotaur em 20 movimentos, algumas paredes do \
labirinto se movem, mudando o layout
- Se Teseu chegar no Minotaur, ele mata Minotaur, e aí pode sair do labirinto

Então precisamos de:

- Uma função para mover o Minotaur, aleatoriamente
- Uma função para mover o Teseu até o Minotaur, temos o bfs pra isso pronto
- Uma função para verificar se Teseu chegou no Minotaur
- Uma função para verificar se Teseu saiu do labirinto
- Uma função para mudar o layout do labirinto, movendo algumas paredes \
(talvez. Mudar paredes aparentemente é complicado,
então talvez a gente só mude o layout do labirinto, gerando um novo labirinto,\
e colocando Teseu e Minotaur em posições aleatórias)'''

'''Vamos criar uma classe GameState para manter o estado do jogo, incluindo as\
posições de Teseu e Minotaur, o número de movimentos restantes, e o layout\
atual do labirinto.'''
