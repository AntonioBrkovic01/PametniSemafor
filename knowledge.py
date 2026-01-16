from collections import deque
from datetime import datetime


class KnowledgeBase:
    def __init__(self):
        self.traffic_history = deque(maxlen=100)
        self.hourly_stats = {i: {'count': 0, 'total_wait': 0} for i in range(24)}
        self.vehicle_types_count = {'CAR': 0, 'BUS': 0, 'AMBULANCE': 0, 'POLICE': 0, 'FIRE': 0}
        self.emergency_events = []
        self.phase_history = deque(maxlen=50)
        self.neighbor_states = {}
        self.green_wave_requests = deque(maxlen=10)
    
    def record_vehicle(self, vehicle_type, wait_time):
        hour = datetime.now().hour
        self.hourly_stats[hour]['count'] += 1
        self.hourly_stats[hour]['total_wait'] += wait_time
        self.vehicle_types_count[vehicle_type] = self.vehicle_types_count.get(vehicle_type, 0) + 1
        self.traffic_history.append({'type': vehicle_type, 'wait': wait_time, 'time': datetime.now()})
    
    def record_phase_change(self, from_phase, to_phase, reason):
        self.phase_history.append({'from': from_phase, 'to': to_phase, 'reason': reason, 'time': datetime.now()})
    
    def record_emergency(self, vehicle_id, vehicle_type, direction):
        self.emergency_events.append({'id': vehicle_id, 'type': vehicle_type, 'dir': direction, 'time': datetime.now()})
    
    def update_neighbor_state(self, neighbor_id, phase, light_state):
        self.neighbor_states[neighbor_id] = {'phase': phase, 'state': light_state, 'time': datetime.now()}
    
    def add_green_wave_request(self, direction, eta):
        self.green_wave_requests.append({'direction': direction, 'eta': eta, 'time': datetime.now()})


class VehicleKnowledgeBase:
    def __init__(self):
        self.intersections_passed = []
        self.wait_times = {}
        self.refused_count = 0
        self.total_requests = 0
    
    def record_intersection(self, intersection_id, wait_time, granted):
        self.intersections_passed.append({'id': intersection_id, 'wait': wait_time, 'granted': granted})
        self.wait_times[intersection_id] = wait_time
        self.total_requests += 1
        if not granted:
            self.refused_count += 1