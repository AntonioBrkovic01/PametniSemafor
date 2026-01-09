import pygame
import config

class TrafficLight:
    def __init__(self, x, y, group):
        self.x = x
        self.y = y
        self.group = group
        self.state = "RED"

    def draw(self, screen, font, seconds_left):
        if self.state == "GREEN":
            color = config.GREEN_LIGHT
        elif self.state == "YELLOW":
            color = config.YELLOW_LIGHT
        else:
            color = config.RED_LIGHT 
        
        center_x = self.x * config.CELL_SIZE + (config.CELL_SIZE // 2)
        center_y = self.y * config.CELL_SIZE + (config.CELL_SIZE // 2)
        radius = config.CELL_SIZE // 2 - 2
        
        pygame.draw.circle(screen, color, (center_x, center_y), radius)

        if self.state != "YELLOW":
            text_surf = font.render(str(seconds_left), True, config.WHITE)
            text_rect = text_surf.get_rect(center=(center_x, center_y - 15))

            bg_rect = text_rect.inflate(4,4)
            pygame.draw.rect(screen, config.BLACK, bg_rect)
            screen.blit(text_surf, text_rect)
