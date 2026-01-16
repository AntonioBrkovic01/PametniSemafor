import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import config
from knowledge import KnowledgeBase, VehicleKnowledgeBase


class VehicleAgent(Agent):
    def __init__(self, jid, password, vehicle_id, vehicle_type, direction, spawn_pos, shared_data):
        super().__init__(jid, password)
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.direction = direction
        self.shared_data = shared_data
        self.is_emergency = vehicle_type in config.EMERGENCY_PRIORITY
        self.priority = config.EMERGENCY_PRIORITY.get(vehicle_type, 999)
        self.knowledge = VehicleKnowledgeBase()
        
        self.x, self.y = float(spawn_pos[0]), float(spawn_pos[1])
        self.speed = config.VEHICLE_SPEEDS.get(vehicle_type, 3)
        self.dx, self.dy = config.DIRECTION_DELTAS[direction]
        self.size = config.VEHICLE_SIZES.get(vehicle_type, (18, 32))
        self.length = self.size[1]
        
        self.waiting_time = 0
        self.is_stopped = False
        self.permissions = {'A': False, 'B': False}
        self.passed_intersections = set()
        self.current_intersection = None
        self.active = True
        self.request_sent = {}
        self.yielding_to_emergency = False
        self.refused_intersections = {}
        
        self.flash_state = True
        self.flash_counter = 0

    class CombinedBehaviour(CyclicBehaviour):
        async def run(self):
            agent = self.agent
            
            if agent.is_emergency and agent.active:
                for int_id, tl_info in config.TRAFFIC_LIGHTS.items():
                    if int_id not in agent.request_sent or not agent.request_sent.get(int_id):
                        msg = Message(to=tl_info['jid'])
                        msg.set_metadata("performative", "request-when")
                        msg.set_metadata("type", "emergency")
                        msg.body = f"{agent.vehicle_id}|{agent.direction}|{agent.vehicle_type}|True|{agent.priority}"
                        await self.send(msg)
                        agent.request_sent[int_id] = True
                        agent.shared_data.messages += 1
                        print(f"[FIPA] {agent.vehicle_id} -> Semafor_{int_id}: REQUEST-WHEN (emergency={agent.vehicle_type}, prioritet={agent.priority})")
                
                agent.shared_data.emergency_active = True
                agent.shared_data.emergency_vehicle_id = agent.vehicle_id
            
            elif not agent.is_emergency:
                nearest = config.get_nearest_intersection(agent.x, agent.y, agent.direction)
                if agent.near_stop_line(nearest) and not agent.permissions.get(nearest) and not agent.request_sent.get(nearest):
                    if nearest not in agent.passed_intersections:
                        tl_info = config.TRAFFIC_LIGHTS[nearest]
                        msg = Message(to=tl_info['jid'])
                        msg.set_metadata("performative", "request")
                        msg.body = f"{agent.vehicle_id}|{agent.direction}|{agent.vehicle_type}|False|999"
                        await self.send(msg)
                        agent.request_sent[nearest] = True
                        agent.shared_data.messages += 1
                        agent.knowledge.total_requests += 1
                        print(f"[FIPA] {agent.vehicle_id} -> Semafor_{nearest}: REQUEST (smjer={agent.direction}, tip={agent.vehicle_type})")
            
            msg = await self.receive(timeout=0.03)
            if msg:
                performative = msg.get_metadata("performative")
                msg_type = msg.get_metadata("type")
                
                if performative == "agree":
                    parts = msg.body.split("|")
                    int_id = parts[1] if len(parts) > 1 else 'A'
                    agent.permissions[int_id] = True
                    agent.request_sent[int_id] = False
                    agent.knowledge.record_intersection(int_id, agent.waiting_time, True)
                    print(f"[FIPA] {agent.vehicle_id} <- Semafor_{int_id}: AGREE (prolaz odobren)")
                
                elif performative == "refuse":
                    parts = msg.body.split("|")
                    int_id = parts[1] if len(parts) > 1 else 'A'
                    reason = parts[2] if len(parts) > 2 else "unknown"
                    agent.refused_intersections[int_id] = reason
                    agent.request_sent[int_id] = False
                    agent.knowledge.refused_count += 1
                    print(f"[FIPA] {agent.vehicle_id} <- Semafor_{int_id}: REFUSE (razlog={reason})")
                
                elif performative == "inform" and msg_type == "emergency_alert":
                    if not agent.is_emergency:
                        agent.yielding_to_emergency = True
                        print(f"[FIPA] {agent.vehicle_id} <- INFORM: EMERGENCY_ALERT (ustupam prednost)")
                
                elif performative == "inform" and msg_type == "emergency_clear":
                    agent.yielding_to_emergency = False
                    print(f"[FIPA] {agent.vehicle_id} <- INFORM: EMERGENCY_CLEAR (nastavljam)")
            
            await asyncio.sleep(0.02)

    async def setup(self):
        self.add_behaviour(self.CombinedBehaviour())

    def get_color(self):
        if self.is_emergency:
            self.flash_counter += 1
            if self.flash_counter >= 6:
                self.flash_counter = 0
                self.flash_state = not self.flash_state
            if self.vehicle_type == 'AMBULANCE':
                return (255, 0, 0) if self.flash_state else (255, 255, 255)
            elif self.vehicle_type == 'POLICE':
                return (0, 0, 255) if self.flash_state else (255, 0, 0)
            elif self.vehicle_type == 'FIRE':
                return (255, 0, 0) if self.flash_state else (255, 165, 0)
        if self.yielding_to_emergency:
            return (150, 150, 150)
        return config.COLORS.get(self.vehicle_type, config.COLORS['CAR'])

    def get_front_position(self):
        if self.direction == 'N': return (self.x, self.y - self.length // 2)
        elif self.direction == 'S': return (self.x, self.y + self.length // 2)
        elif self.direction == 'W': return (self.x - self.length // 2, self.y)
        elif self.direction == 'E': return (self.x + self.length // 2, self.y)
        return (self.x, self.y)

    def near_stop_line(self, intersection_id):
        if intersection_id in self.passed_intersections:
            return False
        stop_line = config.get_stop_line(intersection_id, self.direction)
        front_x, front_y = self.get_front_position()
        ix, iy = config.INTERSECTIONS[intersection_id]
        
        if self.direction == 'N':
            return front_y <= stop_line + 25 and front_y >= stop_line - 10 and abs(self.x - ix) < config.ROAD_WIDTH
        elif self.direction == 'S':
            return front_y >= stop_line - 25 and front_y <= stop_line + 10 and abs(self.x - ix) < config.ROAD_WIDTH
        elif self.direction == 'W':
            return front_x <= stop_line + 25 and front_x >= stop_line - 10
        elif self.direction == 'E':
            return front_x >= stop_line - 25 and front_x <= stop_line + 10
        return False

    def in_intersection_zone(self, intersection_id):
        ix, iy = config.INTERSECTIONS[intersection_id]
        hw = config.ROAD_WIDTH // 2 + 10
        return abs(self.x - ix) < hw and abs(self.y - iy) < hw

    def past_intersection(self, intersection_id):
        ix, iy = config.INTERSECTIONS[intersection_id]
        margin = config.ROAD_WIDTH // 2 + 20
        if self.direction == 'N': return self.y < iy - margin
        elif self.direction == 'S': return self.y > iy + margin
        elif self.direction == 'W': return self.x < ix - margin
        elif self.direction == 'E': return self.x > ix + margin
        return False

    def out_of_bounds(self):
        return self.x < -50 or self.x > config.GRID_WIDTH + 50 or self.y < -50 or self.y > config.GRID_HEIGHT + 50

    def check_collision(self, all_vehicles):
        front_x, front_y = self.get_front_position()
        for v in all_vehicles:
            if v.vehicle_id == self.vehicle_id: continue
            if not v.active: continue
            if self.is_emergency and v.yielding_to_emergency: continue
            
            if self.direction in ['N', 'S'] and v.direction in ['N', 'S']:
                if abs(v.x - self.x) > 25: continue
            elif self.direction in ['W', 'E'] and v.direction in ['W', 'E']:
                if abs(v.y - self.y) > 25: continue
            else:
                continue
                
            if self.direction == 'N' and v.y < front_y and front_y - v.y < config.VEHICLE_GAP: return True
            elif self.direction == 'S' and v.y > front_y and v.y - front_y < config.VEHICLE_GAP: return True
            elif self.direction == 'W' and v.x < front_x and front_x - v.x < config.VEHICLE_GAP: return True
            elif self.direction == 'E' and v.x > front_x and v.x - front_x < config.VEHICLE_GAP: return True
        return False

    def update(self, all_vehicles):
        if not self.active: return
        if self.out_of_bounds():
            self.active = False
            if self.is_emergency:
                self.shared_data.emergency_active = False
                self.shared_data.emergency_vehicle_id = None
            return

        if self.yielding_to_emergency and not self.is_emergency:
            self.is_stopped = True
            return

        for int_id in config.INTERSECTIONS:
            if int_id not in self.passed_intersections and self.past_intersection(int_id):
                self.passed_intersections.add(int_id)
                self.current_intersection = None

        nearest = config.get_nearest_intersection(self.x, self.y, self.direction)
        
        if nearest not in self.passed_intersections:
            if self.in_intersection_zone(nearest):
                self.current_intersection = nearest
                if not self.check_collision(all_vehicles):
                    self.x += self.dx * self.speed
                    self.y += self.dy * self.speed
                return
            
            if self.near_stop_line(nearest):
                if self.is_emergency or self.permissions.get(nearest):
                    self.is_stopped = False
                    self.current_intersection = nearest
                    self.x += self.dx * self.speed
                    self.y += self.dy * self.speed
                else:
                    self.is_stopped = True
                    self.waiting_time += 1
                return

        if not self.check_collision(all_vehicles):
            self.is_stopped = False
            self.x += self.dx * self.speed
            self.y += self.dy * self.speed
        else:
            self.is_stopped = True


class TrafficLightAgent(Agent):
    def __init__(self, jid, password, intersection_id, position, shared_data):
        super().__init__(jid, password)
        self.intersection_id = intersection_id
        self.position = position
        self.shared_data = shared_data
        self.knowledge = KnowledgeBase()
        
        self.current_phase = config.PHASE_NS
        self.timer = config.MAIN_ROAD_GREEN_DURATION
        self.light_state = 'GREEN'
        self.phase_changes = 0
        self.emergency_activations = 0
        self.emergency_mode = False
        self.emergency_vehicle = None
        self.pending_requests = {}
        self.granted_vehicles = set()
        self.vehicles_ref = []
        self.green_wave_pending = None

    class CombinedBehaviour(CyclicBehaviour):
        async def run(self):
            agent = self.agent
            
            msg = await self.receive(timeout=0.02)
            if msg:
                performative = msg.get_metadata("performative")
                msg_type = msg.get_metadata("type")
                
                if performative == "request" or performative == "request-when":
                    parts = msg.body.split("|")
                    content = {
                        'vehicle_id': parts[0],
                        'direction': parts[1],
                        'vehicle_type': parts[2],
                        'is_emergency': parts[3] == 'True',
                        'priority': int(parts[4]),
                        'sender': str(msg.sender)
                    }
                    
                    print(f"[FIPA] Semafor_{agent.intersection_id} <- {content['vehicle_id']}: {performative.upper()} (smjer={content['direction']}, tip={content['vehicle_type']}, emergency={content['is_emergency']})")
                    
                    if content['is_emergency']:
                        if not agent.emergency_mode:
                            agent.emergency_mode = True
                            agent.emergency_vehicle = content
                            agent.emergency_activations += 1
                            agent.knowledge.record_emergency(content['vehicle_id'], content['vehicle_type'], content['direction'])
                            print(f"[STANJE] Semafor_{agent.intersection_id}: EMERGENCY MODE AKTIVIRAN za {content['vehicle_type']}")
                            
                            required = config.PHASE_NS if content['direction'] in config.MAIN_ROAD_DIRECTIONS else config.PHASE_WE
                            if agent.current_phase != required:
                                agent.knowledge.record_phase_change(agent.current_phase, required, "emergency")
                                agent.current_phase = required
                                agent.phase_changes += 1
                                print(f"[STANJE] Semafor_{agent.intersection_id}: Promjena faze -> {'N-S' if required == 0 else 'W-E'}")
                            agent.light_state = 'GREEN'
                            
                            for v in agent.vehicles_ref:
                                if not v.is_emergency and v.active:
                                    alert = Message(to=str(v.jid))
                                    alert.set_metadata("performative", "inform")
                                    alert.set_metadata("type", "emergency_alert")
                                    alert.body = f"YIELD|{content['vehicle_id']}"
                                    await self.send(alert)
                            print(f"[FIPA] Semafor_{agent.intersection_id} -> BROADCAST: INFORM emergency_alert")
                        
                        response = Message(to=content['sender'])
                        response.set_metadata("performative", "agree")
                        response.body = f"{content['vehicle_id']}|{agent.intersection_id}"
                        await self.send(response)
                        print(f"[FIPA] Semafor_{agent.intersection_id} -> {content['vehicle_id']}: AGREE (emergency prioritet)")
                    else:
                        if content['vehicle_id'] not in agent.granted_vehicles:
                            direction = content['direction']
                            color = agent.get_light_color(direction)
                            
                            if agent.emergency_mode:
                                response = Message(to=content['sender'])
                                response.set_metadata("performative", "refuse")
                                response.body = f"{content['vehicle_id']}|{agent.intersection_id}|emergency_active"
                                await self.send(response)
                                agent.shared_data.messages += 1
                                print(f"[FIPA] Semafor_{agent.intersection_id} -> {content['vehicle_id']}: REFUSE (emergency aktivan)")
                            elif color != 'GREEN':
                                response = Message(to=content['sender'])
                                response.set_metadata("performative", "refuse")
                                response.body = f"{content['vehicle_id']}|{agent.intersection_id}|red_light"
                                await self.send(response)
                                agent.shared_data.messages += 1
                                agent.pending_requests[content['vehicle_id']] = content
                                print(f"[FIPA] Semafor_{agent.intersection_id} -> {content['vehicle_id']}: REFUSE (crveno) - dodan u pending")
                            else:
                                agent.pending_requests[content['vehicle_id']] = content
                
                elif performative == "inform" and msg_type == "neighbor_state":
                    parts = msg.body.split("|")
                    neighbor_id = parts[0]
                    phase = int(parts[1])
                    state = parts[2]
                    agent.knowledge.update_neighbor_state(neighbor_id, phase, state)
                
                elif performative == "inform" and msg_type == "green_wave":
                    parts = msg.body.split("|")
                    direction = parts[0]
                    eta = int(parts[1])
                    agent.knowledge.add_green_wave_request(direction, eta)
                    agent.green_wave_pending = {'direction': direction, 'eta': eta}
            
            to_remove = []
            for vehicle_id, req in agent.pending_requests.items():
                if req.get('is_emergency'): continue
                if vehicle_id in agent.granted_vehicles: continue
                
                direction = req['direction']
                color = agent.get_light_color(direction)
                
                if color == 'GREEN' and not agent.emergency_mode:
                    response = Message(to=req['sender'])
                    response.set_metadata("performative", "agree")
                    response.body = f"{vehicle_id}|{agent.intersection_id}"
                    await self.send(response)
                    agent.granted_vehicles.add(vehicle_id)
                    agent.knowledge.record_vehicle(req['vehicle_type'], 0)
                    to_remove.append(vehicle_id)
                    print(f"[FIPA] Semafor_{agent.intersection_id} -> {vehicle_id}: AGREE (iz pending - zeleno)")
            
            for vid in to_remove:
                del agent.pending_requests[vid]
            
            await asyncio.sleep(0.02)

    async def setup(self):
        self.add_behaviour(self.CombinedBehaviour())

    def get_green_duration(self):
        return config.MAIN_ROAD_GREEN_DURATION if self.current_phase == config.PHASE_NS else config.SIDE_ROAD_GREEN_DURATION

    def get_light_color(self, direction):
        if self.emergency_mode and self.emergency_vehicle:
            return 'GREEN' if direction == self.emergency_vehicle['direction'] else 'RED'
        is_main = direction in config.MAIN_ROAD_DIRECTIONS
        is_my_phase = (self.current_phase == config.PHASE_NS) if is_main else (self.current_phase == config.PHASE_WE)
        return self.light_state if is_my_phase else 'RED'

    def get_timer_seconds(self):
        return self.timer / config.FPS

    def count_waiting(self, vehicles, road_type):
        directions = config.MAIN_ROAD_DIRECTIONS if road_type == 'main' else config.SIDE_ROAD_DIRECTIONS
        count = 0
        ix, iy = self.position
        for v in vehicles:
            if v.direction in directions and v.active:
                if v.direction in ['N', 'S'] and abs(v.x - ix) < config.ROAD_WIDTH:
                    if v.direction == 'N' and v.y > iy:
                        count += config.BUS_VEHICLE_EQUIVALENT if v.vehicle_type == 'BUS' else 1
                    elif v.direction == 'S' and v.y < iy:
                        count += config.BUS_VEHICLE_EQUIVALENT if v.vehicle_type == 'BUS' else 1
                elif v.direction in ['W', 'E']:
                    if v.direction == 'W' and v.x > ix:
                        count += config.BUS_VEHICLE_EQUIVALENT if v.vehicle_type == 'BUS' else 1
                    elif v.direction == 'E' and v.x < ix:
                        count += config.BUS_VEHICLE_EQUIVALENT if v.vehicle_type == 'BUS' else 1
        return count

    def check_green_wave(self, vehicles):
        if self.green_wave_pending:
            direction = self.green_wave_pending['direction']
            eta = self.green_wave_pending['eta']
            if eta <= 0:
                required_phase = config.PHASE_WE if direction in config.SIDE_ROAD_DIRECTIONS else config.PHASE_NS
                if self.current_phase != required_phase and self.light_state == 'GREEN':
                    self.light_state = 'YELLOW'
                    self.timer = config.YELLOW_DURATION
                    self.knowledge.record_phase_change(self.current_phase, required_phase, "green_wave")
                self.green_wave_pending = None
            else:
                self.green_wave_pending['eta'] -= 1

    def update(self, vehicles):
        self.vehicles_ref = vehicles
        
        active_ids = {v.vehicle_id for v in vehicles if v.active}
        self.granted_vehicles = self.granted_vehicles & active_ids
        
        if self.emergency_mode:
            emergency_still_active = False
            for v in vehicles:
                if v.is_emergency and v.active and not v.past_intersection(self.intersection_id):
                    emergency_still_active = True
                    break
            
            if not emergency_still_active:
                self.emergency_mode = False
                self.emergency_vehicle = None
                print(f"[STANJE] Semafor_{self.intersection_id}: EMERGENCY MODE DEAKTIVIRAN")
            return

        self.check_green_wave(vehicles)
        
        self.timer -= 1

        if self.light_state == 'YELLOW':
            if self.timer <= 0:
                old_phase = self.current_phase
                self.current_phase = (self.current_phase + 1) % 2
                self.light_state = 'GREEN'
                self.timer = self.get_green_duration()
                self.phase_changes += 1
                self.knowledge.record_phase_change(old_phase, self.current_phase, "timer")
                print(f"[STANJE] Semafor_{self.intersection_id}: Faza {'N-S' if self.current_phase == 0 else 'W-E'} -> ZELENO ({self.get_timer_seconds():.0f}s)")
            return

        if self.timer <= 0:
            self.light_state = 'YELLOW'
            self.timer = config.YELLOW_DURATION
            print(f"[STANJE] Semafor_{self.intersection_id}: -> ŽUTO (2s)")
            return

        main_count = self.count_waiting(vehicles, 'main')
        side_count = self.count_waiting(vehicles, 'side')
        
        if self.current_phase == config.PHASE_WE:
            if main_count >= config.MAIN_ROAD_QUEUE_THRESHOLD and side_count == 0:
                self.light_state = 'YELLOW'
                self.timer = config.YELLOW_DURATION
                self.knowledge.record_phase_change(self.current_phase, config.PHASE_NS, "adaptive_main_priority")
                print(f"[ADAPTIVNO] Semafor_{self.intersection_id}: Prioritet glavnoj cesti (čeka {main_count} vozila)")
        elif self.current_phase == config.PHASE_NS:
            if side_count >= config.SIDE_ROAD_QUEUE_THRESHOLD and main_count == 0:
                self.light_state = 'YELLOW'
                self.timer = config.YELLOW_DURATION
                self.knowledge.record_phase_change(self.current_phase, config.PHASE_WE, "adaptive_side_priority")
                print(f"[ADAPTIVNO] Semafor_{self.intersection_id}: Prioritet sporednoj cesti (čeka {side_count} vozila)")

    def grant_permissions_sync(self, vehicles):
        for v in vehicles:
            if v.is_emergency:
                v.permissions[self.intersection_id] = True
                continue
                
            if v.near_stop_line(self.intersection_id) and not v.permissions.get(self.intersection_id):
                color = self.get_light_color(v.direction)
                if color == 'GREEN' and not self.emergency_mode:
                    v.permissions[self.intersection_id] = True
                    self.granted_vehicles.add(v.vehicle_id)
                    self.knowledge.record_vehicle(v.vehicle_type, v.waiting_time)