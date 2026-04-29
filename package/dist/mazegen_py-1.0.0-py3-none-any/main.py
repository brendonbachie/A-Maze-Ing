import mazegen

mz = mazegen.MazeGenerator(20, 20, "maze.txt", True, (0, 0), (19, 19))
mz.generate()
