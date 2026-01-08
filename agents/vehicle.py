class Vehicle:
    def __init__(self, vehicle_id, x, y, dx, dy):
        self.id = vehicle_id
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

        self.symbol = "V"

    def move(self, semafor):
        stop_x = 9
        stop_y = 9

        should_stop = False
        
        if self.dx > 0:
            if self.x == stop_x and semafor.state == "RED":
                should_stop = True
        elif self.dy > 0:
            if self.y == stop_y and semafor.state == "RED":
                should_stop = True
        if not should_stop:
            self.x += self.dx
            self.y += self.dy
        else:
            pass
            

    def is_on_road(self, width, height):
        return 0 <= self.x < width and 0 <= self.y < height
    