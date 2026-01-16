GRID_WIDTH = 1200
GRID_HEIGHT = 800
FPS = 60
ROAD_WIDTH = 60

INTERSECTIONS = {
    'A': (400, 400),
    'B': (800, 400),
}

MAIN_ROAD_DIRECTIONS = ['N', 'S']
SIDE_ROAD_DIRECTIONS = ['W', 'E']

MAIN_ROAD_GREEN_DURATION = 1800
SIDE_ROAD_GREEN_DURATION = 900
YELLOW_DURATION = 120

MAIN_ROAD_QUEUE_THRESHOLD = 3
SIDE_ROAD_QUEUE_THRESHOLD = 4
BUS_VEHICLE_EQUIVALENT = 3
VEHICLE_GAP = 45

SPAWN_RATE_MAIN = 0.004
SPAWN_RATE_SIDE = 0.002
EMERGENCY_SPAWN_RATE = 0.0005

PHASE_NS = 0
PHASE_WE = 1

COLORS = {
    'GRASS': (34, 139, 34),
    'ROAD': (50, 50, 50),
    'ROAD_MAIN': (60, 60, 60),
    'INTERSECTION': (70, 70, 70),
    'LINE': (255, 255, 0),
    'LINE_WHITE': (255, 255, 255),
    'CAR': (0, 100, 255),
    'BUS': (255, 165, 0),
    'AMBULANCE': (255, 200, 200),
    'POLICE': (0, 0, 139),
    'FIRE': (178, 34, 34),
    'RED': (255, 0, 0),
    'YELLOW': (255, 255, 0),
    'GREEN': (0, 255, 0),
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'SELECTED': (255, 0, 255),
}

VEHICLE_SPEEDS = {'CAR': 3, 'BUS': 2, 'AMBULANCE': 5, 'POLICE': 5, 'FIRE': 5}
VEHICLE_SIZES = {'CAR': (18, 32), 'BUS': (22, 50), 'AMBULANCE': (20, 38), 'POLICE': (20, 36), 'FIRE': (24, 46)}
EMERGENCY_PRIORITY = {'AMBULANCE': 1, 'FIRE': 2, 'POLICE': 3}

DIRECTION_DELTAS = {'N': (0, -1), 'S': (0, 1), 'W': (-1, 0), 'E': (1, 0)}

XMPP_SERVER = "localhost"

TRAFFIC_LIGHTS = {
    'A': {'jid': 'semafor_a@localhost', 'password': 'semafor123', 'pos': (400, 400), 'neighbors': ['B']},
    'B': {'jid': 'semafor_b@localhost', 'password': 'semafor123', 'pos': (800, 400), 'neighbors': ['A']},
}

GREEN_WAVE_DELAY = 180
DISTANCE_BETWEEN_INTERSECTIONS = 400


def get_spawn_positions():
    return {
        'N_A': (INTERSECTIONS['A'][0] - ROAD_WIDTH//4, GRID_HEIGHT - 30),
        'N_B': (INTERSECTIONS['B'][0] - ROAD_WIDTH//4, GRID_HEIGHT - 30),
        'S_A': (INTERSECTIONS['A'][0] + ROAD_WIDTH//4, 30),
        'S_B': (INTERSECTIONS['B'][0] + ROAD_WIDTH//4, 30),
        'W': (GRID_WIDTH - 30, 400 + ROAD_WIDTH//4),
        'E': (30, 400 - ROAD_WIDTH//4),
    }


def get_stop_line(intersection_id, direction):
    ix, iy = INTERSECTIONS[intersection_id]
    hw = ROAD_WIDTH // 2
    lines = {
        'N': iy + hw + 15,
        'S': iy - hw - 15,
        'W': ix + hw + 15,
        'E': ix - hw - 15,
    }
    return lines[direction]


def get_nearest_intersection(x, y, direction):
    if direction in ['N', 'S']:
        min_dist = float('inf')
        nearest = 'A'
        for int_id, (ix, iy) in INTERSECTIONS.items():
            dist = abs(x - ix)
            if dist < min_dist:
                min_dist = dist
                nearest = int_id
        return nearest
    else:
        if direction == 'E':
            for int_id in ['A', 'B']:
                ix, iy = INTERSECTIONS[int_id]
                if x < ix:
                    return int_id
            return 'B'
        else:
            for int_id in ['B', 'A']:
                ix, iy = INTERSECTIONS[int_id]
                if x > ix:
                    return int_id
            return 'A'