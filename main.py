from environment.grid import TrafficGrid

def main():
    print("Inicijalizacija simulacije")

    cesta = TrafficGrid()

    cesta.update_position(10, 10, "X")

    cesta.display()

if __name__ == "__main__":
    main()