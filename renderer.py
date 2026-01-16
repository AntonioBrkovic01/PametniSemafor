import pygame
import config


class Renderer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.GRID_WIDTH, config.GRID_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Pametni Semafor - SPADE Multi-Agent System")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.running = True
        self.fullscreen = False
        self.spawn_selector = None
        self.status_message = None
        self.status_timer = 0

    def set_spawn_selector(self, selector):
        self.spawn_selector = selector

    def set_status(self, message, duration=180):
        self.status_message = message
        self.status_timer = duration

    def handle_events(self):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((config.GRID_WIDTH, config.GRID_HEIGHT), pygame.RESIZABLE)
                else:
                    events.append(event)
        return events

    def draw_road(self):
        self.screen.fill(config.COLORS['GRASS'])
        pygame.draw.rect(self.screen, config.COLORS['ROAD'], (0, 400 - config.ROAD_WIDTH//2, config.GRID_WIDTH, config.ROAD_WIDTH))
        for int_id, (ix, iy) in config.INTERSECTIONS.items():
            pygame.draw.rect(self.screen, config.COLORS['ROAD_MAIN'], (ix - config.ROAD_WIDTH//2, 0, config.ROAD_WIDTH, config.GRID_HEIGHT))
            pygame.draw.rect(self.screen, config.COLORS['INTERSECTION'], (ix - config.ROAD_WIDTH//2, iy - config.ROAD_WIDTH//2, config.ROAD_WIDTH, config.ROAD_WIDTH))
        for i in range(0, config.GRID_WIDTH, 30):
            in_intersection = False
            for int_id, (ix, iy) in config.INTERSECTIONS.items():
                if abs(i - ix) < config.ROAD_WIDTH//2 + 5:
                    in_intersection = True
                    break
            if not in_intersection:
                pygame.draw.line(self.screen, config.COLORS['LINE_WHITE'], (i, 400), (i + 15, 400), 2)
        for int_id, (ix, iy) in config.INTERSECTIONS.items():
            for j in range(0, config.GRID_HEIGHT, 30):
                if abs(j - iy) > config.ROAD_WIDTH//2 + 5:
                    pygame.draw.line(self.screen, config.COLORS['LINE'], (ix, j), (ix, j + 15), 2)
        self.screen.blit(self.small_font.render("GLAVNA (A)", True, config.COLORS['WHITE']), (config.INTERSECTIONS['A'][0] - 35, 30))
        self.screen.blit(self.small_font.render("GLAVNA (B)", True, config.COLORS['WHITE']), (config.INTERSECTIONS['B'][0] - 35, 30))
        self.screen.blit(self.small_font.render("SPOREDNA", True, config.COLORS['WHITE']), (config.GRID_WIDTH - 90, 400 - config.ROAD_WIDTH//2 - 20))

    def draw_traffic_lights(self, traffic_lights):
        for tl in traffic_lights:
            ix, iy = tl.position
            positions = {
                'N': (ix - config.ROAD_WIDTH//2 - 35, iy + config.ROAD_WIDTH//2 + 5),
                'S': (ix + config.ROAD_WIDTH//2 + 5, iy - config.ROAD_WIDTH//2 - 40),
                'W': (ix + config.ROAD_WIDTH//2 + 5, iy + config.ROAD_WIDTH//2 + 5),
                'E': (ix - config.ROAD_WIDTH//2 - 35, iy - config.ROAD_WIDTH//2 - 40),
            }
            timer_positions = {
                'N': (ix - config.ROAD_WIDTH//2 - 60, iy + config.ROAD_WIDTH//2 + 55),
                'S': (ix + config.ROAD_WIDTH//2 + 5, iy - config.ROAD_WIDTH//2 - 70),
                'W': (ix + config.ROAD_WIDTH//2 + 40, iy + config.ROAD_WIDTH//2 + 20),
                'E': (ix - config.ROAD_WIDTH//2 - 60, iy - config.ROAD_WIDTH//2 - 25),
            }
            for direction, pos in positions.items():
                pygame.draw.rect(self.screen, config.COLORS['BLACK'], (pos[0], pos[1], 30, 45))
                color = tl.get_light_color(direction)
                red = config.COLORS['RED'] if color == 'RED' else (80, 0, 0)
                yellow = config.COLORS['YELLOW'] if color == 'YELLOW' else (80, 80, 0)
                green = config.COLORS['GREEN'] if color == 'GREEN' else (0, 80, 0)
                pygame.draw.circle(self.screen, red, (pos[0] + 15, pos[1] + 10), 6)
                pygame.draw.circle(self.screen, yellow, (pos[0] + 15, pos[1] + 23), 6)
                pygame.draw.circle(self.screen, green, (pos[0] + 15, pos[1] + 36), 6)
                if tl.emergency_mode:
                    pygame.draw.rect(self.screen, (255, 0, 255), (pos[0]-2, pos[1]-2, 34, 49), 2)
                timer_text = f"{tl.get_timer_seconds():.0f}s"
                if color == 'GREEN':
                    timer_color = config.COLORS['GREEN']
                elif color == 'YELLOW':
                    timer_color = config.COLORS['YELLOW']
                else:
                    timer_color = config.COLORS['RED']
                tpos = timer_positions[direction]
                timer_surface = self.small_font.render(timer_text, True, timer_color)
                self.screen.blit(timer_surface, tpos)
            label = self.font.render(f"{tl.intersection_id}", True, config.COLORS['WHITE'])
            self.screen.blit(label, (ix - 6, iy - 10))

    def draw_vehicle(self, v):
        w, h = (v.size[0], v.size[1]) if v.direction in ['N', 'S'] else (v.size[1], v.size[0])
        rect = pygame.Rect(int(v.x) - w//2, int(v.y) - h//2, w, h)
        pygame.draw.rect(self.screen, v.get_color(), rect)
        pygame.draw.rect(self.screen, config.COLORS['BLACK'], rect, 1)
        if v.is_emergency:
            pygame.draw.rect(self.screen, config.COLORS['WHITE'], rect, 2)
        if v.is_stopped and not v.is_emergency:
            pygame.draw.circle(self.screen, config.COLORS['RED'], (int(v.x), int(v.y) - h//2 - 4), 3)

    def draw_stats(self, stats, traffic_lights):
        lines = [
            f"Aktivnih: {stats['active']}",
            f"Proslo: {stats['passed']}",
            f"Prosj. cekanje: {stats['avg_wait']:.1f}s",
            f"Max cekanje: {stats['max_wait']:.1f}s",
            f"FIPA poruka: {stats['messages']}",
            f"Emergency: {'DA' if stats['emergency'] else 'NE'}",
            "",
        ]
        for tl in traffic_lights:
            lines.append(f"Sem {tl.intersection_id}: faze={tl.phase_changes} hitno={tl.emergency_activations}")
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (5, 5, 240, len(lines) * 20 + 10))
        for i, line in enumerate(lines):
            self.screen.blit(self.small_font.render(line, True, config.COLORS['WHITE']), (10, 10 + i * 20))

    def draw_controls(self):
        lines = [
            "=== SPAWN VOZILA ===",
            "SPACE - Auto",
            "B - Autobus",
            "1 - Hitna",
            "2 - Vatrogasci",
            "3 - Policija",
            "",
            "Nakon odabira tipa:",
            "A/B - raskrižje",
            "N/S/W/E - smjer",
            "",
            "F11 - Fullscreen",
            "ESC - Izlaz"
        ]
        y = config.GRID_HEIGHT - len(lines) * 18 - 10
        pygame.draw.rect(self.screen, (0, 0, 0), (5, y - 5, 200, len(lines) * 18 + 10))
        for i, line in enumerate(lines):
            color = config.COLORS['YELLOW'] if "===" in line else config.COLORS['WHITE']
            self.screen.blit(self.small_font.render(line, True, color), (10, y + i * 18))

    def draw_spawn_status(self):
        if self.spawn_selector and self.spawn_selector.is_active():
            status = self.spawn_selector.get_status_text()
            if status:
                text_surface = self.font.render(status, True, config.COLORS['WHITE'])
                bg_rect = pygame.Rect(config.GRID_WIDTH//2 - 200, 10, 400, 35)
                pygame.draw.rect(self.screen, config.COLORS['SELECTED'], bg_rect)
                pygame.draw.rect(self.screen, config.COLORS['WHITE'], bg_rect, 2)
                self.screen.blit(text_surface, (config.GRID_WIDTH//2 - 190, 18))
                if self.spawn_selector.selected_intersection:
                    ix, iy = config.INTERSECTIONS[self.spawn_selector.selected_intersection]
                    pygame.draw.rect(self.screen, config.COLORS['SELECTED'], (ix - config.ROAD_WIDTH//2 - 5, iy - config.ROAD_WIDTH//2 - 5, config.ROAD_WIDTH + 10, config.ROAD_WIDTH + 10), 4)
        if self.status_timer > 0:
            self.status_timer -= 1
            if self.status_message:
                text_surface = self.font.render(self.status_message, True, config.COLORS['GREEN'])
                bg_rect = pygame.Rect(config.GRID_WIDTH//2 - 150, config.GRID_HEIGHT - 50, 300, 30)
                pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
                self.screen.blit(text_surface, (config.GRID_WIDTH//2 - 140, config.GRID_HEIGHT - 45))

    def draw_legend(self):
        items = [
            ("AUTO", config.COLORS['CAR']),
            ("AUTOBUS", config.COLORS['BUS']),
            ("HITNA", (255, 100, 100)),
            ("POLICIJA", config.COLORS['POLICE']),
            ("VATROGASCI", config.COLORS['FIRE'])
        ]
        x = config.GRID_WIDTH - 120
        y = 60
        pygame.draw.rect(self.screen, (0, 0, 0), (x - 5, y - 5, 115, len(items) * 22 + 10))
        for i, (name, color) in enumerate(items):
            pygame.draw.rect(self.screen, color, (x, y + i * 22, 16, 16))
            self.screen.blit(self.small_font.render(name, True, config.COLORS['WHITE']), (x + 22, y + i * 22))

    def render(self, vehicles, traffic_lights, stats):
        self.draw_road()
        self.draw_traffic_lights(traffic_lights)
        for v in vehicles:
            if v.active:
                self.draw_vehicle(v)
        self.draw_stats(stats, traffic_lights)
        self.draw_controls()
        self.draw_legend()
        self.draw_spawn_status()
        pygame.display.flip()
        self.clock.tick(config.FPS)
        return self.running

    def quit(self):
        pygame.quit()