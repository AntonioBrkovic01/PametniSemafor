import pygame
import random
import config
from agents.vehicle import Vehicle
from agents.traffic_light import TrafficLight

def main():
    pygame.init()
    pygame.font.init() 
    
    timer_font = pygame.font.SysFont('Arial', 12, bold=True)
    
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Glavna vs Sporedna Cesta")
    clock = pygame.time.Clock()

    semafori = [
        TrafficLight(x=19, y=13, group='horizontal'),
        TrafficLight(x=22, y=12, group='horizontal'),
        TrafficLight(x=21, y=11, group='vertical'), 
        TrafficLight(x=20, y=14, group='vertical')  
    ]

    timer = 0
    phase = "VERT_GREEN" 
    
    MAIN_ROAD_TIME = 220
    SIDE_ROAD_TIME = 110 
    YELLOW_TIME = 20     
    
    current_limit = MAIN_ROAD_TIME 

    vozila = []
    id_counter = 1
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        timer += 1
        
        if timer > current_limit:
            timer = 0
            
            if phase == "VERT_GREEN":
                phase = "VERT_YELLOW"
                current_limit = YELLOW_TIME 
            
            elif phase == "VERT_YELLOW":
                phase = "HORZ_GREEN"
                current_limit = SIDE_ROAD_TIME 
            
            elif phase == "HORZ_GREEN":
                phase = "HORZ_YELLOW"
                current_limit = YELLOW_TIME
            
            elif phase == "HORZ_YELLOW":
                phase = "VERT_GREEN"
                current_limit = MAIN_ROAD_TIME
            
            print(f"Faza: {phase} | Trajanje: {current_limit/config.FPS}s")

        seconds_left = int((current_limit - timer) / config.FPS) + 1

        for s in semafori:
            if s.group == 'horizontal':
                if phase == "HORZ_GREEN": s.state = "GREEN"
                elif phase == "HORZ_YELLOW": s.state = "YELLOW"
                else: s.state = "RED"
            
            elif s.group == 'vertical':
                if phase == "VERT_GREEN": s.state = "GREEN"
                elif phase == "VERT_YELLOW": s.state = "YELLOW"
                else: s.state = "RED"

        if random.random() < 0.2:
            opcije = (['desno', 'lijevo', 'dolje', 'gore'])
            vjerojatnosti = [10,10,40,40]
            smjer = random.choices(opcije,weights=vjerojatnosti, k=1)[0]
            novi = None
            
            if smjer == 'desno': novi = Vehicle(id_counter, 0, 13, 1, 0, config.PURPLE_CAR)
            elif smjer == 'lijevo': novi = Vehicle(id_counter, config.GRID_WIDTH-1, 12, -1, 0, config.PURPLE_CAR)
            elif smjer == 'dolje': novi = Vehicle(id_counter, 21, 0, 0, 1, config.RED_CAR)
            elif smjer == 'gore': novi = Vehicle(id_counter, 20, config.GRID_HEIGHT-1, 0, -1, config.RED_CAR)
            
            if novi:
                vozila.append(novi)
                id_counter += 1

        vozila = [v for v in vozila if v.is_on_road(config.GRID_WIDTH, config.GRID_HEIGHT)]
        for auto in vozila: auto.move(semafori, vozila)

        screen.fill(config.GREEN_GRASS)
        
        pygame.draw.rect(screen, config.GRAY_ROAD, (0, 12*config.CELL_SIZE, config.SCREEN_WIDTH, 2*config.CELL_SIZE))
        pygame.draw.rect(screen, config.GRAY_ROAD, (20*config.CELL_SIZE, 0, 2*config.CELL_SIZE, config.SCREEN_HEIGHT))

        for x in range(0, config.SCREEN_WIDTH, 40):
            pygame.draw.line(screen, config.WHITE, (x, 13*config.CELL_SIZE), (x+20, 13*config.CELL_SIZE), 1)
        for y in range(0, config.SCREEN_HEIGHT, 40):
            pygame.draw.line(screen, config.WHITE, (21*config.CELL_SIZE, y), (21*config.CELL_SIZE, y+20), 1)

        for s in semafori: 
            s.draw(screen, timer_font, seconds_left)
            
        for auto in vozila: auto.draw(screen)

        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()