class Vehicle:
    def __init__(self, vehicle_id, x, y):
        self.id = vehicle_id
        self.x = x
        self.y = y
        self.symbol = "V"

    def move(self):
        self.x += 1
    