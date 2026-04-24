import random
import main
from validate_config import read_config_file, Configuration
from map import Cell, MazeGenerator, maze_generator, game_maze_generator

class GameState:
    def __init__(self, config: Configuration):
        self.config = config
        self.maze: MazeGenerator = None
        self.teseu_pos = self.config.teseu
        self.minotauro_pos = self.config.minotauro
        self.exit_pos = self.config.exit
        self.teseu_moves = 20
        self.minotauro_moves = 10
        self.teseu_idx = 0
        self.minotauro_idx = 0
        self.teseu_path: list[Cell] = []
        self.minotauro_path: list[Cell] = []
        self.game_over = False
        self.teseu_wins = False

#cria objeto com configurações do jogo



#criar o labirinto com teseu de entrada e minotauro como saída
def generate_game_state(configs: Configuration) -> GameState:
    crete = GameState(configs)
    crete.maze = game_maze_generator(configs)
    crete.teseu_pos = crete.maze.get_cell(configs.teseu[0], configs.teseu[1]) #coloca o teseu na posição de entrada do labirinto
    crete.minotauro_pos = crete.maze.get_cell(configs.minotauro[0], configs.minotauro[1]) #coloca o minotauro em uma posição aleatória do labirinto
    crete.exit_pos = crete.maze.get_cell(configs.exit[0], configs.exit[1]) #coloca a saída do labirinto
    teseu_path = crete.maze.bfs_game(crete.teseu_pos, crete.minotauro_pos)
    # for i, cell in enumerate(teseu_path):
    #     if i <= 20:
    #         crete.teseu_path.append(cell)
    crete.minotauro_path = crete.maze.bfs_game(crete.minotauro_pos, crete.exit_pos)
    # for i, cell in enumerate(minotauro_path):
    #     if i <= 10:
    #         crete.minotauro_path.append(cell)
    return crete

'''Enquanto o caminho (index) < 20, se ele for % 2 == 0, move o minotauro e teseu, se for % 2 == 1, move só o teseu.
diminui o número de movimentos do minotauro e do teseu, e verifica se o teseu chegou no minotauro. 
Se não chegou, pega a posição de teseu, config.entry = posição de teseu, config.exit = posição do minotauro, 
gera um mapa novo, adiciona movimentos do minotauro e do teseu, e continua o loop. Se chegou, teseu ganha, 
e aí ele busca a saída do labirinto'''






'''Aqui vai ficar a questão do jogo, o teseu e o minotauro, a mudança de labirinto e as regras 

A principio, Teseu tera 20 movimentos no labirinto e minotauro 10. Pela mitologia original, 
Teseu matou o minotauro e saiu do labirinto. Então temos basicamente:
- Teseu tem 20 movimentos
- Minotauro tem 10 movimentos
- Se Teseu não chegar no Minotauro em 20 movimentos, algumas paredes do labirinto se movem, mudando o layout
- Se Teseu chegar no Minotauro, ele mata Minotauro, e aí pode sair do labirinto

Então precisamos de:

- Uma função para mover o Minotauro, aleatoriamente
- Uma função para mover o Teseu até o Minotauro, temos o bfs pra isso pronto
- Uma função para verificar se Teseu chegou no Minotauro
- Uma função para verificar se Teseu saiu do labirinto
- Uma função para mudar o layout do labirinto, movendo algumas paredes (talvez. Mudar paredes aparentemente é complicado, 
então talvez a gente só mude o layout do labirinto, gerando um novo labirinto, e colocando Teseu e Minotauro em posições aleatórias)'''

'''Vamos criar uma classe GameState para manter o estado do jogo, incluindo as posições de Teseu e Minotauro, o número de movimentos restantes, e o layout atual do labirinto.'''