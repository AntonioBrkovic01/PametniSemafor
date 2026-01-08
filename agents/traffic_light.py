class TrafficLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = "RED"
        self.timer = 0

    def update(self):
        self.timer += 1
        
        if self.timer > 10:
            self.timer = 0
            if self.state == "RED":
                self.state = "GREEN"
            else:
                self.state = "RED"
    @property
    def symbol(self):
        return "R" if self.state == "RED" else "G"