class Vehicle:
    def __init__(self, vehicle_id, x, y, dx, dy):
        self.id = vehicle_id
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

        self.symbol = "V"

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def is_on_road(self, width, height):
        return 0 <= self.x < width and 0 <= self.y < height
    