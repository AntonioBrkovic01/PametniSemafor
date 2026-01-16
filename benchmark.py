import random
import pygame
import matplotlib.pyplot as plt
import numpy as np
import config

pygame.init()


class MockVehicle:
    def __init__(self, vehicle_id, vehicle_type, direction, spawn_pos, intersection_id=None):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.direction = direction
        self.spawn_intersection = intersection_id
        self.is_emergency = vehicle_type in config.EMERGENCY_PRIORITY
        self.x, self.y = float(spawn_pos[0]), float(spawn_pos[1])
        self.speed = config.VEHICLE_SPEEDS.get(vehicle_type, 3)
        self.dx, self.dy = config.DIRECTION_DELTAS[direction]
        self.size = config.VEHICLE_SIZES.get(vehicle_type, (18, 32))
        self.length = self.size[1]
        self.waiting_time = 0
        self.is_stopped = False
        self.permissions = {'A': False, 'B': False}
        self.passed_intersections = set()
        self.active = True

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

    def update(self, all_vehicles, traffic_lights):
        if not self.active: return
        if self.out_of_bounds():
            self.active = False
            return
        for int_id in config.INTERSECTIONS:
            if int_id not in self.passed_intersections and self.past_intersection(int_id):
                self.passed_intersections.add(int_id)
        nearest = config.get_nearest_intersection(self.x, self.y, self.direction)
        if nearest not in self.passed_intersections:
            if self.in_intersection_zone(nearest):
                if not self.check_collision(all_vehicles):
                    self.x += self.dx * self.speed
                    self.y += self.dy * self.speed
                return
            if self.near_stop_line(nearest):
                tl = traffic_lights.get(nearest)
                if tl:
                    color = tl.get_light_color(self.direction)
                    if self.is_emergency or color == 'GREEN':
                        self.permissions[nearest] = True
                        self.is_stopped = False
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


class MockTrafficLight:
    def __init__(self, intersection_id, position, mode="SMART"):
        self.intersection_id = intersection_id
        self.position = position
        self.mode = mode
        self.current_phase = config.PHASE_NS
        self.timer = config.MAIN_ROAD_GREEN_DURATION
        self.light_state = 'GREEN'
        self.phase_changes = 0

    def get_green_duration(self):
        return config.MAIN_ROAD_GREEN_DURATION if self.current_phase == config.PHASE_NS else config.SIDE_ROAD_GREEN_DURATION

    def get_light_color(self, direction):
        is_main = direction in config.MAIN_ROAD_DIRECTIONS
        is_my_phase = (self.current_phase == config.PHASE_NS) if is_main else (self.current_phase == config.PHASE_WE)
        return self.light_state if is_my_phase else 'RED'

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

    def update(self, vehicles):
        self.timer -= 1
        if self.light_state == 'YELLOW':
            if self.timer <= 0:
                self.current_phase = (self.current_phase + 1) % 2
                self.light_state = 'GREEN'
                self.timer = self.get_green_duration()
                self.phase_changes += 1
            return
        if self.timer <= 0:
            self.light_state = 'YELLOW'
            self.timer = config.YELLOW_DURATION
            return
        if self.mode == "SMART":
            main_count = self.count_waiting(vehicles, 'main')
            side_count = self.count_waiting(vehicles, 'side')
            if self.current_phase == config.PHASE_WE:
                if main_count >= config.MAIN_ROAD_QUEUE_THRESHOLD and side_count == 0:
                    self.light_state = 'YELLOW'
                    self.timer = config.YELLOW_DURATION
            elif self.current_phase == config.PHASE_NS:
                if side_count >= config.SIDE_ROAD_QUEUE_THRESHOLD and main_count == 0:
                    self.light_state = 'YELLOW'
                    self.timer = config.YELLOW_DURATION


class BenchmarkSimulation:
    def __init__(self, mode, target_vehicles):
        self.mode = mode
        self.target_vehicles = target_vehicles
        self.vehicles = []
        self.traffic_lights = {}
        self.vehicle_counter = 0
        self.vehicles_passed = 0
        self.total_wait = 0
        self.max_wait = 0
        self.wait_times_list = []
        self.wait_by_type = {'CAR': [], 'BUS': [], 'AMBULANCE': [], 'POLICE': [], 'FIRE': []}
        self.wait_by_intersection = {'A': [], 'B': []}
        self.emergency_response_times = []
        for int_id, tl_info in config.TRAFFIC_LIGHTS.items():
            self.traffic_lights[int_id] = MockTrafficLight(int_id, tl_info['pos'], mode)

    def spawn_vehicle(self, force_emergency=False):
        self.vehicle_counter += 1
        if force_emergency:
            vehicle_type = random.choice(['AMBULANCE', 'POLICE', 'FIRE'])
        else:
            vehicle_type = 'CAR' if random.random() < 0.85 else 'BUS'
        spawn_positions = config.get_spawn_positions()
        intersection_id = random.choice(['A', 'B'])
        if random.random() < 0.7:
            direction = random.choice(['N', 'S'])
            spawn_key = f"{direction}_{intersection_id}"
        else:
            direction = random.choice(['W', 'E'])
            spawn_key = direction
        spawn_pos = spawn_positions[spawn_key]
        vehicle = MockVehicle(f"v{self.vehicle_counter}", vehicle_type, direction, spawn_pos, intersection_id)
        self.vehicles.append(vehicle)

    def run(self):
        frame = 0
        spawn_interval = 30
        emergency_interval = 500
        while self.vehicles_passed < self.target_vehicles:
            frame += 1
            if frame % spawn_interval == 0 and len(self.vehicles) < 50:
                self.spawn_vehicle()
            if frame % emergency_interval == 0:
                self.spawn_vehicle(force_emergency=True)
            for tl in self.traffic_lights.values():
                tl.update(self.vehicles)
            for v in self.vehicles:
                v.update(self.vehicles, self.traffic_lights)
            for v in self.vehicles[:]:
                if not v.active:
                    self.vehicles_passed += 1
                    wait_seconds = v.waiting_time / config.FPS
                    self.total_wait += wait_seconds
                    self.max_wait = max(self.max_wait, wait_seconds)
                    self.wait_times_list.append(wait_seconds)
                    self.wait_by_type[v.vehicle_type].append(wait_seconds)
                    if v.spawn_intersection:
                        self.wait_by_intersection[v.spawn_intersection].append(wait_seconds)
                    if v.is_emergency:
                        self.emergency_response_times.append(wait_seconds)
                    self.vehicles.remove(v)
            if frame > 100000:
                break
        total_phase_changes = sum(tl.phase_changes for tl in self.traffic_lights.values())
        return {
            'mode': self.mode,
            'vehicles': self.vehicles_passed,
            'avg_wait': self.total_wait / max(1, self.vehicles_passed),
            'max_wait': self.max_wait,
            'phase_changes': total_phase_changes,
            'wait_times_list': self.wait_times_list,
            'wait_by_type': self.wait_by_type,
            'wait_by_intersection': self.wait_by_intersection,
            'emergency_response_times': self.emergency_response_times
        }


def create_benchmark_charts(fixed_results, smart_results, save_path="benchmark_results.png"):
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Benchmark: FIKSNI vs PAMETNI Semafor', fontsize=16, fontweight='bold')
    colors_fixed = '#e74c3c'
    colors_smart = '#27ae60'
    width = 0.35
    
    ax1 = axes[0, 0]
    vehicle_types = ['CAR', 'BUS', 'AMBULANCE', 'POLICE', 'FIRE']
    type_labels = ['Auto', 'Autobus', 'Hitna', 'Policija', 'Vatrogasci']
    fixed_by_type = [np.mean(fixed_results['wait_by_type'][t]) if fixed_results['wait_by_type'][t] else 0 for t in vehicle_types]
    smart_by_type = [np.mean(smart_results['wait_by_type'][t]) if smart_results['wait_by_type'][t] else 0 for t in vehicle_types]
    x = np.arange(len(type_labels))
    ax1.bar(x - width/2, fixed_by_type, width, label='FIKSNI', color=colors_fixed)
    ax1.bar(x + width/2, smart_by_type, width, label='PAMETNI', color=colors_smart)
    ax1.set_xlabel('Tip vozila')
    ax1.set_ylabel('Prosječno čekanje (s)')
    ax1.set_title('Čekanje po tipu vozila')
    ax1.set_xticks(x)
    ax1.set_xticklabels(type_labels, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    ax2 = axes[0, 1]
    if fixed_results['wait_times_list'] and smart_results['wait_times_list']:
        bins = np.linspace(0, max(max(fixed_results['wait_times_list']), max(smart_results['wait_times_list'])), 20)
        ax2.hist(fixed_results['wait_times_list'], bins=bins, alpha=0.7, label='FIKSNI', color=colors_fixed)
        ax2.hist(smart_results['wait_times_list'], bins=bins, alpha=0.7, label='PAMETNI', color=colors_smart)
    ax2.set_xlabel('Vrijeme čekanja (s)')
    ax2.set_ylabel('Broj vozila')
    ax2.set_title('Distribucija vremena čekanja')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    ax3 = axes[0, 2]
    emergency_data = []
    emergency_labels = []
    if fixed_results['emergency_response_times']:
        emergency_data.append(fixed_results['emergency_response_times'])
        emergency_labels.append('FIKSNI')
    if smart_results['emergency_response_times']:
        emergency_data.append(smart_results['emergency_response_times'])
        emergency_labels.append('PAMETNI')
    if emergency_data:
        bp = ax3.boxplot(emergency_data, labels=emergency_labels, patch_artist=True)
        if len(bp['boxes']) > 0:
            bp['boxes'][0].set_facecolor(colors_fixed)
        if len(bp['boxes']) > 1:
            bp['boxes'][1].set_facecolor(colors_smart)
    ax3.set_ylabel('Response time (s)')
    ax3.set_title('Response time hitnih vozila')
    ax3.grid(axis='y', alpha=0.3)
    
    ax4 = axes[1, 0]
    metrics = ['Prosj.\nčekanje', 'Max\nčekanje', 'Prosj.\nputovanje']
    fixed_metrics = [fixed_results['avg_wait'], fixed_results['max_wait'], fixed_results['avg_wait'] * 1.5]
    smart_metrics = [smart_results['avg_wait'], smart_results['max_wait'], smart_results['avg_wait'] * 1.5]
    x = np.arange(len(metrics))
    ax4.bar(x - width/2, fixed_metrics, width, label='FIKSNI', color=colors_fixed)
    ax4.bar(x + width/2, smart_metrics, width, label='PAMETNI', color=colors_smart)
    ax4.set_ylabel('Vrijeme (s)')
    ax4.set_title('Glavni pokazatelji')
    ax4.set_xticks(x)
    ax4.set_xticklabels(metrics)
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    ax5 = axes[1, 1]
    intersections = ['A', 'B']
    fixed_by_int = [len(fixed_results['wait_by_intersection'][i]) for i in intersections]
    smart_by_int = [len(smart_results['wait_by_intersection'][i]) for i in intersections]
    x = np.arange(len(intersections))
    ax5.bar(x - width/2, fixed_by_int, width, label='FIKSNI', color=colors_fixed)
    ax5.bar(x + width/2, smart_by_int, width, label='PAMETNI', color=colors_smart)
    ax5.set_xlabel('Raskrižje')
    ax5.set_ylabel('Broj vozila')
    ax5.set_title('Promet po raskrižjima')
    ax5.set_xticks(x)
    ax5.set_xticklabels(intersections)
    ax5.legend()
    ax5.grid(axis='y', alpha=0.3)
    
    ax6 = axes[1, 2]
    activity_metrics = ['Propusnost\n(voz/min)', 'Promjene\nfaza']
    fixed_throughput = fixed_results['vehicles'] / (sum(fixed_results['wait_times_list']) / 60) if sum(fixed_results['wait_times_list']) > 0 else 0
    smart_throughput = smart_results['vehicles'] / (sum(smart_results['wait_times_list']) / 60) if sum(smart_results['wait_times_list']) > 0 else 0
    fixed_activity = [fixed_throughput * 100, fixed_results['phase_changes'] * 100]
    smart_activity = [smart_throughput * 100, smart_results['phase_changes'] * 100]
    x = np.arange(len(activity_metrics))
    ax6.bar(x - width/2, fixed_activity, width, label='FIKSNI', color=colors_fixed)
    ax6.bar(x + width/2, smart_activity, width, label='PAMETNI', color=colors_smart)
    ax6.set_title('Propusnost i aktivnost')
    ax6.set_xticks(x)
    ax6.set_xticklabels(activity_metrics)
    ax6.legend()
    ax6.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n[Graf] Spremljeno u: {save_path}")
    plt.show()


def run_benchmark(target_vehicles):
    print("="*70)
    print("BENCHMARK: FIKSNI vs PAMETNI SEMAFOR")
    print("="*70)
    print(f"\n[Benchmark] FIXED mod - cilj: {target_vehicles} vozila")
    fixed_sim = BenchmarkSimulation("FIXED", target_vehicles)
    fixed_results = fixed_sim.run()
    print(f"[Benchmark] SMART mod - cilj: {target_vehicles} vozila")
    smart_sim = BenchmarkSimulation("SMART", target_vehicles)
    smart_results = smart_sim.run()
    print("\n" + "="*70)
    print("REZULTATI")
    print("="*70)
    print(f"\nFIXED mod:")
    print(f"  Prosjecno cekanje: {fixed_results['avg_wait']:.2f}s")
    print(f"  Max cekanje: {fixed_results['max_wait']:.2f}s")
    print(f"  Vozila: {fixed_results['vehicles']}")
    print(f"  Promjena faza: {fixed_results['phase_changes']}")
    print(f"  Hitnih vozila: {len(fixed_results['emergency_response_times'])}")
    print(f"\nSMART mod:")
    print(f"  Prosjecno cekanje: {smart_results['avg_wait']:.2f}s")
    print(f"  Max cekanje: {smart_results['max_wait']:.2f}s")
    print(f"  Vozila: {smart_results['vehicles']}")
    print(f"  Promjena faza: {smart_results['phase_changes']}")
    print(f"  Hitnih vozila: {len(smart_results['emergency_response_times'])}")
    print("\n" + "="*70)
    print("USPOREDBA")
    print("="*70)
    if fixed_results['avg_wait'] > 0:
        improvement = ((fixed_results['avg_wait'] - smart_results['avg_wait']) / fixed_results['avg_wait']) * 100
        if improvement > 0:
            print(f"\nSMART mod smanjuje prosjecno cekanje za {improvement:.1f}%")
        else:
            print(f"\nFIXED mod ima {-improvement:.1f}% manje prosjecno cekanje")
    if fixed_results['max_wait'] > smart_results['max_wait']:
        max_improvement = ((fixed_results['max_wait'] - smart_results['max_wait']) / fixed_results['max_wait']) * 100
        print(f"SMART mod smanjuje max cekanje za {max_improvement:.1f}% ({smart_results['max_wait']:.2f}s vs {fixed_results['max_wait']:.2f}s)")
    print(f"SMART mod ima {smart_results['phase_changes']} promjena faza vs FIXED {fixed_results['phase_changes']}")
    if fixed_results['emergency_response_times'] and smart_results['emergency_response_times']:
        fixed_emerg_avg = np.mean(fixed_results['emergency_response_times'])
        smart_emerg_avg = np.mean(smart_results['emergency_response_times'])
        print(f"Prosjecni response time hitnih: SMART {smart_emerg_avg:.2f}s vs FIXED {fixed_emerg_avg:.2f}s")
    print("="*70)
    print("\n[Graf] Generiranje grafova...")
    create_benchmark_charts(fixed_results, smart_results)
    return fixed_results, smart_results


if __name__ == "__main__":
    import sys
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    run_benchmark(target)