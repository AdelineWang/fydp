class Coordinator:
    def __init__(self, road):
        self.road = road
    
    def update(self):
        vehicle = self.road.vehicles['red']
        vehicle.x = 423
        vehicle.y = 290
        vehicle.heading = 0.0
        self.road.update_positions()
