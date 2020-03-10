class StraightRoad:
    """Model for a straight road.

    Two lane road that is horizontal in the input image centered vertically.
    The lanes are offset from the center line by an amount specified.
    """
    def __init__(self, calib, lane_offset, vehicles):
        self.pixel_width, self.pixel_height = calib.calc_distance_per_pixel()

        # Road and lane locations
        self.center_line = calib.image_height / 2
        pixel_lane_offset = lane_offset / self.pixel_height
        lane0_center_line = self.center_line - pixel_lane_offset
        lane1_center_line = self.center_line + pixel_lane_offset
        self.lane_center_lines = [lane0_center_line, lane1_center_line]
        self.road_len = calib.fov_width

        # Dictionary for road objects
        self.vehicles = {}
        self.sorted_vehicles = [[], []]
        for vehicle in vehicles:
            self.vehicles[vehicle.name] = vehicle
            self.sorted_vehicles[0].append(vehicle.name)

    def update_positions(self):
        for vehicle in self.vehicles.values():
            vehicle.longitude = vehicle.x * self.pixel_width

            lane_center_line = self.lane_center_lines[vehicle.lane]
            latitude_pixel_delta = vehicle.y - lane_center_line
            vehicle.latitude = latitude_pixel_delta * self.pixel_width
            print(vehicle.name + ' (long, lat) = ' + str((vehicle.longitude, vehicle.latitude)))

    def update_connections(self):
        for lane in range(len(self.sorted_vehicles)):
            self.sorted_vehicles[lane].sort(
                key=lambda name: self.vehicles[name].longitude,
                reverse=True)

            lane_vehicles = self.sorted_vehicles[lane]
            for (i, name) in enumerate(lane_vehicles):
                veh = self.vehicles[name]
                veh.leader = lane_vehicles[i - 1] if i > 0 else None
                if i < len(lane_vehicles) - 1:
                    veh.lag = lane_vehicles[i + 1]
                else:
                    veh.lag = None

    def calc_accel(self, dt):
        self.update_connections()
        for i, name in enumerate(self.sorted_vehicles[0]):
            veh = self.vehicles[name]
            speed = veh.speed

            leader = veh.leader
            if leader is None:
                s = self.road_len
                veh.accel = veh.long_model.calc_accel(s, speed, 0, 0)
                veh.update(dt)
            else:
                veh_lead = self.vehicles[leader]
                speed_lead = veh_lead.speed
                accel_lead = veh_lead.accel
                s = veh_lead.longitude - veh.longitude
                veh.accel = veh.long_model.calc_accel(s, speed, speed_lead,
                                                      accel_lead)
                veh.update(dt)
