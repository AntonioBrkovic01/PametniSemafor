import numpy as np
import config

class TrafficGrid:
    def __init__(self):
        self.width = config.GRID_WIDTH
        self.height = config.GRID_HEIGHT

        self.grid = np.full((self.height, self.width), config.SYMBOL_EMPTY)

    def display(self):
        """Ispisuje trenutno stanje mreze u terminalu."""
        print("-" * (self.width * 2))

        for row in self.grid:
            print(" ".join(row))

        print("-" * (self.width * 2))

    def update_position(self, x, y, symbol):
        """Postavlja simbol na odredenu koordinatu"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = symbol