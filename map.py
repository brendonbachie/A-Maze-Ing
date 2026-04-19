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
    def __init__(self, width: int, height: int, entry: tuple, exit: tuple, perfect: bool):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.maze = [[Cell(x, y) for x in range(width)] for y in range(height)]

'''Pegar celula "inicio", marca como visitada, 
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
