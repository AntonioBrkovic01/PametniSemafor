import numpy as np
import config

class TrafficGrid:
    def __init__(self):
        self.width = config.GRID_WIDTH
        self.height = config.GRID_HEIGHT
        
        self.grid = np.full((self.height, self.width), config.SYMBOL_GRASS)
        
        horizontalne_trake = [8, 9, 18, 19]  
        vertikalne_trake = [10, 11, 30, 31] 

        for y in range(self.height):
            for x in range(self.width):
                if y in horizontalne_trake or x in vertikalne_trake:
                    self.grid[y][x] = config.SYMBOL_ROAD

    def update_position(self, x, y, symbol):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = symbol

    def display(self):
        
        print("═" * (self.width * 2)) 
        for row in self.grid:
            line = " ".join(row)
            print(line)
        print("═" * (self.width * 2)) 