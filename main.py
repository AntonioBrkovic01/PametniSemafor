import time
import os
from environment.grid import TrafficGrid
from agents.vehicle import Vehicle
import config

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    cesta = TrafficGrid()
    auto = Vehicle(vehicle_id=1, x=0, y=10)

    print("Pocinje simulacija")
    time.sleep(1)

    for korak in range(15):
        clear_screen()

        cesta = TrafficGrid()
        cesta.update_position(auto.x, auto.y, auto.symbol)

        print(f"Korak: {korak +1}")
        cesta.display()

        auto.move()

        time.sleep(0.5)

    print("Kraj")

if __name__ == "__main__":
    main()