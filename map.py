import validate_config

class Cell():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.north = True
        self.south = True
        self.east = True
        self.west = True
        self.visited = False

class MazeGenerator():
    def __init__(self, configuration: validate_config.Configuration):
        self.width = configuration.width
        self.height = configuration.height
        self.entry = configuration.entry
        self.exit = configuration.exit
        self.perfect = configuration.perfect
        self.maze = [Cell(x, y) for x in range(self.width) for y in range(self.height)]

'''
DFS

Pegar celula "inicio", marca como visitada, 
fazer lista de vizinhos, verificar x e y negativos, maior que o limite ou visitada com if, se for, não colocar na lista,
random[(x+1, x-1, y+1, y-1)], pega o vizinho e remove a parede entre elas de ambos.'''

#regras de remoção de paredes

'''se x da celula atual for maior que x da celula vizinha, entao a parede 
oeste da celula atual é removida e a parede leste da celula vizinha é removida.''' 

''' Se x da celula atual for menor que x da celula vizinha, entao a parede leste da 
 celula atual é removida e a parede oeste da celula vizinha é removida. '''

'''Se y da celula atual for maior que y da celula vizinha, entao a parede norte da 
 celula atual é removida e a parede sul da celula vizinha é removida.''' 

'''Se y da celula atual for menor que y da celula vizinha, entao a parede sul 
 da celula atual é removida e a parede norte da celula vizinha é removida.'''

'''Verificar lista de vizinhos, se tiver, escolher um vizinho aleatório, remover a parede entre eles,
marcar o vizinho como visitado, e chamar a função recursivamente com o vizinho como nova celula atual.
Se não tiver vizinhos, voltar para a celula (return na função) anterior e repetir o processo.'''

'''

BFS

Pega a célula de início, marca ela como visitada e coloca seus vizinhos em uma fila (no caso seria a mesma coisa do DFS, [(x+1, x-1, y+1, y-1)], verificando os limites e se já foi visitada).
Enquanto a fila não tiver vazia, pega o primeiro vizinho, coloca o vizinho dele na fila, marca ele como visitado e remove da fila. A fila funciona com FIFO, então sabemos que
sempre vamos pegar um vizinho do nível atual antes de pegar um vizinho do próximo nível. Seguimos fazendo isso até a fica ficar vazia, ou seja, até visitar todas as células.
Usarei o bfs pra resolução do labirinto, pra encontrar a saida, e o DFS pra gerar o labirinto, porque o DFS é mais fácil de implementar, e o BFS é mais fácil de garantir 
que a solução encontrada seja a mais curta, já que o labirinto é gerado aleatoriamente, não tem como garantir que a solução encontrada pelo DFS seja a mais curta, então vou 
usar o BFS mesmo.
'''