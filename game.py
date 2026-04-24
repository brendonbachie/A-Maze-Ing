import random
import main
import validate_config
import map

class GameState:
    def __init__(self, config):
        self.config = config
        #self.maze = map.Maze(self.config.width, self.config.height, self.config.seed)
        self.teseu_pos = self.config.entry
        self.minotauro_pos = self.config.exit
        self.teseu_moves = 20
        self.minotauro_moves = 10
        self. teseu_path = []
        self.game_over = False
        self.teseu_wins = False

#cria objeto com configurações do jogo


configs = validate_config.read_config_file()
crete = GameState(configs)

#criar o labirinto com teseu de entrada e minotauro como saída 
maze = map.maze_generator(configs)
crete.maze = maze
crete.teseu_pos = configs.entry
crete.minotauro_pos = configs.exit
crete.teseu_path = maze.bfs_game(maze, crete.teseu_pos, crete.minotauro_pos)






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