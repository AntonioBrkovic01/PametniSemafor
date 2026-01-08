import pygame
import random
import config
from agents.vehicle import Vehicle
from agents.traffic_light import TrafficLight

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Simulacija Prometa")
    clock = pygame.time.Clock()

    semafori = [
        TrafficLight(x=19, y=13, group='horizontal'),
        TrafficLight(x=22, y=12, group='horizontal'),
        TrafficLight(x=21, y=11, group='vertical'),
        TrafficLight(x=20, y=14, group='vertical')
    ]

    timer = 0
    phase = "HORZ_GREEN"
    
    vozila = []
    id_counter = 1
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        timer += 1
        if timer > 40:
            timer = 0
            if phase == "HORZ_GREEN":
                phase = "VERT_GREEN"
            else:
                phase = "HORZ_GREEN"
        
        for s in semafori:
            if phase == "HORZ_GREEN":
                s.state = "GREEN" if s.group == 'horizontal' else "RED"
            else:
                s.state = "GREEN" if s.group == 'vertical' else "RED"

        if random.random() < 0.2:
            smjer = random.choice(['desno', 'lijevo', 'dolje', 'gore'])
            novi = None
            
            if smjer == 'desno':
                novi = Vehicle(id_counter, 0, 13, 1, 0, config.PURPLE_CAR)
            elif smjer == 'lijevo':
                novi = Vehicle(id_counter, config.GRID_WIDTH-1, 12, -1, 0, config.PURPLE_CAR)
            elif smjer == 'dolje':
                novi = Vehicle(id_counter, 21, 0, 0, 1, config.RED_CAR)
            elif smjer == 'gore':
                novi = Vehicle(id_counter, 20, config.GRID_HEIGHT-1, 0, -1, config.RED_CAR)
            
            if novi:
                vozila.append(novi)
                id_counter += 1

        vozila = [v for v in vozila if v.is_on_road(config.GRID_WIDTH, config.GRID_HEIGHT)]
        for auto in vozila:
            auto.move(semafori, vozila)

        screen.fill(config.GREEN_GRASS)
        
        pygame.draw.rect(screen, config.GRAY_ROAD, (0, 12*config.CELL_SIZE, config.SCREEN_WIDTH, 2*config.CELL_SIZE))
        pygame.draw.rect(screen, config.GRAY_ROAD, (20*config.CELL_SIZE, 0, 2*config.CELL_SIZE, config.SCREEN_HEIGHT))

        for x in range(0, config.SCREEN_WIDTH, 40):
            pygame.draw.line(screen, config.WHITE, (x, 13*config.CELL_SIZE), (x+20, 13*config.CELL_SIZE), 1)
        for y in range(0, config.SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, config.WHITE, (21*config.CELL_SIZE, y), (21*config.CELL_SIZE, y+20), 1)

        for s in semafori: s.draw(screen)
        for auto in vozila: auto.draw(screen)

        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()