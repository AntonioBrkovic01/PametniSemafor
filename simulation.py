import random
import asyncio
import pygame
import spade
import config
from agents import VehicleAgent, TrafficLightAgent
from renderer import Renderer


class SharedData:
    def __init__(self):
        self.messages = 0
        self.emergency_active = False
        self.emergency_vehicle_id = None


class SpawnSelector:
    def __init__(self):
        self.selected_intersection = None
        self.selected_direction = None
        self.vehicle_type = None
        self.awaiting_intersection = False
        self.awaiting_direction = False
    
    def start_selection(self, vehicle_type):
        self.vehicle_type = vehicle_type
        self.selected_intersection = None
        self.selected_direction = None
        self.awaiting_intersection = True
        self.awaiting_direction = False
    
    def select_intersection(self, intersection):
        if intersection in ['A', 'B']:
            self.selected_intersection = intersection
            self.awaiting_intersection = False
            self.awaiting_direction = True
    
    def select_direction(self, direction):
        if direction in ['N', 'S', 'W', 'E']:
            self.selected_direction = direction
            self.awaiting_direction = False
            return self.get_spawn_info()
        return None
    
    def get_spawn_info(self):
        if self.selected_intersection and self.selected_direction:
            return {'intersection': self.selected_intersection, 'direction': self.selected_direction, 'vehicle_type': self.vehicle_type}
        return None
    
    def reset(self):
        self.selected_intersection = None
        self.selected_direction = None
        self.vehicle_type = None
        self.awaiting_intersection = False
        self.awaiting_direction = False
    
    def is_active(self):
        return self.awaiting_intersection or self.awaiting_direction
    
    def get_status_text(self):
        if self.awaiting_intersection:
            return f"Spawn {self.vehicle_type}: Odaberi raskrižje (A/B)"
        elif self.awaiting_direction:
            return f"Spawn {self.vehicle_type} @ {self.selected_intersection}: Odaberi smjer (N/S/W/E)"
        return None


class Simulation:
    def __init__(self):
        self.traffic_lights = []
        self.vehicles = []
        self.vehicle_counter = 0
        self.vehicles_passed = 0
        self.renderer = Renderer()
        self.max_waiting = 0
        self.shared_data = SharedData()
        self.spawn_selector = SpawnSelector()
        self.renderer.set_spawn_selector(self.spawn_selector)

    async def start_traffic_lights(self):
        for int_id, tl_info in config.TRAFFIC_LIGHTS.items():
            tl = TrafficLightAgent(
                tl_info['jid'],
                tl_info['password'],
                int_id,
                tl_info['pos'],
                self.shared_data
            )
            await tl.start()
            self.traffic_lights.append(tl)
            print(f"[INIT] TrafficLightAgent {int_id} pokrenut na {tl_info['jid']}")

    async def spawn_vehicle(self, vehicle_type, intersection_id, direction):
        self.vehicle_counter += 1
        
        spawn_positions = config.get_spawn_positions()
        
        if direction in ['N', 'S']:
            spawn_key = f"{direction}_{intersection_id}"
        else:
            spawn_key = direction
        
        spawn_pos = spawn_positions[spawn_key]
        
        jid = f"vozilo{self.vehicle_counter}@localhost"
        password = "vozilo123"
        agent = VehicleAgent(jid, password, f"v{self.vehicle_counter}", vehicle_type, direction, spawn_pos, self.shared_data)
        await agent.start()
        await asyncio.sleep(0.05)
        self.vehicles.append(agent)
        
        self.renderer.set_status(f"Spawnan {vehicle_type} @ {intersection_id} smjer {direction}")

    async def spawn_random_vehicle(self, vehicle_type=None):
        if vehicle_type is None:
            vehicle_type = 'CAR' if random.random() < 0.85 else 'BUS'
        
        intersection_id = random.choice(['A', 'B'])
        
        if random.random() < 0.7:
            direction = random.choice(['N', 'S'])
        else:
            direction = random.choice(['W', 'E'])
        
        await self.spawn_vehicle(vehicle_type, intersection_id, direction)

    def get_stats(self):
        active = [v for v in self.vehicles if v.active]
        total_wait = sum(v.waiting_time for v in active)
        self.max_waiting = max(self.max_waiting, max((v.waiting_time for v in active), default=0))
        
        return {
            'active': len(active),
            'passed': self.vehicles_passed,
            'avg_wait': total_wait / len(active) / config.FPS if active else 0,
            'max_wait': self.max_waiting / config.FPS,
            'messages': self.shared_data.messages,
            'emergency': self.shared_data.emergency_active,
        }

    async def handle_input(self, event):
        key = event.key
        
        if self.spawn_selector.is_active():
            if self.spawn_selector.awaiting_intersection:
                if key == pygame.K_a:
                    self.spawn_selector.select_intersection('A')
                elif key == pygame.K_b:
                    self.spawn_selector.select_intersection('B')
                elif key == pygame.K_ESCAPE:
                    self.spawn_selector.reset()
                    self.renderer.set_status("Spawn otkazan")
            elif self.spawn_selector.awaiting_direction:
                direction = None
                if key == pygame.K_n:
                    direction = 'N'
                elif key == pygame.K_s:
                    direction = 'S'
                elif key == pygame.K_w:
                    direction = 'W'
                elif key == pygame.K_e:
                    direction = 'E'
                elif key == pygame.K_ESCAPE:
                    self.spawn_selector.reset()
                    self.renderer.set_status("Spawn otkazan")
                    return
                
                if direction:
                    info = self.spawn_selector.select_direction(direction)
                    if info:
                        await self.spawn_vehicle(info['vehicle_type'], info['intersection'], info['direction'])
                        self.spawn_selector.reset()
            return
        
        if key == pygame.K_SPACE:
            self.spawn_selector.start_selection('CAR')
        elif key == pygame.K_b:
            self.spawn_selector.start_selection('BUS')
        elif key == pygame.K_1:
            self.spawn_selector.start_selection('AMBULANCE')
        elif key == pygame.K_2:
            self.spawn_selector.start_selection('FIRE')
        elif key == pygame.K_3:
            self.spawn_selector.start_selection('POLICE')

    async def run(self):
        print("="*60)
        print("PAMETNI SEMAFOR - Višeagentni sustav")
        print("="*60)
        
        await self.start_traffic_lights()
        
        print("[INIT] Simulacija pokrenuta")
        print("="*60)
        
        while self.renderer.running:
            events = self.renderer.handle_events()
            for e in events:
                if e.type == pygame.KEYDOWN:
                    await self.handle_input(e)

            if random.random() < config.SPAWN_RATE_MAIN:
                await self.spawn_random_vehicle()
            if random.random() < config.SPAWN_RATE_SIDE:
                await self.spawn_random_vehicle()
            if random.random() < config.EMERGENCY_SPAWN_RATE:
                await self.spawn_random_vehicle(random.choice(['AMBULANCE', 'FIRE', 'POLICE']))

            for tl in self.traffic_lights:
                tl.update(self.vehicles)
                tl.grant_permissions_sync(self.vehicles)

            if self.shared_data.emergency_active:
                for v in self.vehicles:
                    if not v.is_emergency and v.active:
                        v.yielding_to_emergency = True
            else:
                for v in self.vehicles:
                    v.yielding_to_emergency = False

            for v in self.vehicles:
                v.update(self.vehicles)

            for v in self.vehicles[:]:
                if not v.active:
                    self.vehicles_passed += 1
                    await v.stop()
                    self.vehicles.remove(v)

            if not self.renderer.render(self.vehicles, self.traffic_lights, self.get_stats()):
                break

            await asyncio.sleep(0.001)

        print("="*60)
        print("Simulacija završena")
        print(f"Ukupno prošlo vozila: {self.vehicles_passed}")
        print(f"FIPA poruka razmijeneno: {self.shared_data.messages}")
        print("="*60)

        for v in self.vehicles:
            await v.stop()
        for tl in self.traffic_lights:
            await tl.stop()
        self.renderer.quit()


async def main():
    sim = Simulation()
    await sim.run()


if __name__ == "__main__":
    spade.run(main())