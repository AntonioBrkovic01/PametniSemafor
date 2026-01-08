import time
import os
import random
from environment.grid import TrafficGrid
from agents.vehicle import Vehicle
from agents.traffic_light import TrafficLight

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    WIDTH = 20
    HEIGHT = 20
    vozila = []
    semafor = TrafficLight(x=9, y=9)
    id_counter = 1

    print("Pocinje simulacija")
    time.sleep(1)

    for korak in range(100):
        clear_screen()
        cesta = TrafficGrid()

        semafor.update()

        if random.random() < 0.3:
            if random.choice(['horizontal', 'vertical']) == 'horizontal':
                novi_auto = Vehicle(id_counter, x=0, y=10, dx=1, dy=0)
                novi_auto.symbol = ">"
            else:
                novi_auto = Vehicle(id_counter, x=10, y=0, dx=0, dy=1)
                novi_auto.symbol = "v"
            vozila.append(novi_auto)
            id_counter += 1
            
        vozila = [v for v in vozila if v.is_on_road(WIDTH, HEIGHT)]

        for auto in vozila:
            cesta.update_position(auto.x, auto.y, auto.symbol)
            auto.move(semafor)
        
        cesta.update_position(semafor.x, semafor.y, semafor.symbol)

        print(f"Korak: {korak + 1} | Broj vozila: {len(vozila)} | Semafor: {semafor.state}")
        cesta.display()
        
        time.sleep(0.3)

    print("Kraj")

if __name__ == "__main__":
    main()