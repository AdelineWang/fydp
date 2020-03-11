import math

import cv2

class Coordinator:
    def __init__(self, road, processor):
        self.road = road
        self.processor = processor

    def update(self):
        vehicle = self.road.vehicles['red']
        vehicle.x = 423
        vehicle.y = 290
        vehicle.heading = 0.0

        vehicle = self.road.vehicles['green']
        vehicle.x = 900
        vehicle.y = 320
        vehicle.heading = 1.2

        self.road.update_positions()
        self.road.calc_accel(0.1)

        # Grab the frame which needs to be processed
        image = cv2.imread('overheadreal.jpg')

        (midpoint, bearing) = self.processor.process_image(image)
        vehicle = self.road.vehicles['red']
        vehicle.x = int(midpoint[0])
        vehicle.y = int(midpoint[1])
        vehicle.heading = bearing
        self.road.update_positions()

    def change_lane(self, name, target_lane):
        self.road.vehicles[name].request_lane_change(target_lane)

    def sim_update(self, dt):
        self.road.update_positions()
        self.road.update_lane_change()

        pixel_width = self.road.pixel_width
        pixel_height = self.road.pixel_height
        for veh in self.road.vehicles.values():
            veh.heading += veh.speed / veh.axle_length \
                * math.tan(veh.steering) * dt
            veh.steer_model.normalize_angle(veh.heading)

            d = veh.speed * dt + 0.5 * veh.accel * dt * dt
            veh.x += d * math.cos(veh.heading) / pixel_width
            veh.y += d * math.sin(veh.heading) / pixel_height

        self.road.calc_accel(dt)
        self.road.calc_speed(dt)
        self.road.calc_steering()
