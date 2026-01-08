import pygame
import config

class TrafficLight:
    def __init__(self, x, y, group):
        self.x = x
        self.y = y
        self.group = group
        self.state = "RED"

    def draw(self, screen):
        color = config.GREEN_LIGHT if self.state == "GREEN" else config.RED_LIGHT
        
        center_x = self.x * config.CELL_SIZE + (config.CELL_SIZE // 2)
        center_y = self.y * config.CELL_SIZE + (config.CELL_SIZE // 2)
        radius = config.CELL_SIZE // 2 - 2
        
        pygame.draw.circle(screen, color, (center_x, center_y), radius)