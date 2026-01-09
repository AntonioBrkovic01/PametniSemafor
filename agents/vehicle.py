import pygame
import config

class Vehicle:
    def __init__(self, vehicle_id, x, y, dx, dy, color):
        self.id = vehicle_id
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color

    def move(self, lista_semafora, sva_vozila):
        next_x = self.x + self.dx
        next_y = self.y + self.dy
        should_stop = False

        for s in lista_semafora:
            if next_x == s.x and next_y == s.y:
                if s.state == "RED" or s.state == "YELLOW":
                    should_stop = True
                    break

        if not should_stop:
            for v in sva_vozila:
                if v.id != self.id and v.x == next_x and v.y == next_y:
                    should_stop = True
                    break

        if not should_stop:
            self.x = next_x
            self.y = next_y

    def is_on_road(self, width, height):
        return 0 <= self.x < width and 0 <= self.y < height

    def draw(self, screen):
        rect = pygame.Rect(
            self.x * config.CELL_SIZE + 2,
            self.y * config.CELL_SIZE + 2,
            config.CELL_SIZE - 4,
            config.CELL_SIZE - 4
        )
        pygame.draw.rect(screen, self.color, rect, width=0)