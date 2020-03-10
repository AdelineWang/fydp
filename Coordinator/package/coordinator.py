import cv2

class Coordinator:
    def __init__(self, road, processor):
        self.road = road
        self.processor = processor

    def update(self):
        # Grab the frame which needs to be processed
        image = cv2.imread('overheadreal.jpg')        
        
        (midpoint, bearing) = self.processor.process_image(image)
        vehicle = self.road.vehicles['red']
        vehicle.x = int(midpoint[0])
        vehicle.y = int(midpoint[1])    
        vehicle.heading = bearing
        self.road.update_positions()
