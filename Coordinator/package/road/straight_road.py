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
            self.sorted_vehicles[vehicle.lane].append(vehicle.name)
        self.update_connections()

    def update_positions(self):
        for vehicle in self.vehicles.values():
            vehicle.longitude = vehicle.x * self.pixel_width

            lane_center_line = self.lane_center_lines[vehicle.lane]
            latitude_pixel_delta = vehicle.y - lane_center_line
            vehicle.latitude = latitude_pixel_delta * self.pixel_width

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
        for lane in range(len(self.sorted_vehicles)):
            for i, name in enumerate(self.sorted_vehicles[lane]):
                veh = self.vehicles[name]
                speed = veh.speed

                leader = veh.leader
                if leader is None:
                    veh.accel = veh.long_model.calc_accel(100, speed, 0, 0)
                else:
                    veh_lead = self.vehicles[leader]
                    speed_lead = veh_lead.speed
                    accel_lead = veh_lead.accel
                    s = veh_lead.longitude - veh.longitude
                    veh.accel = veh.long_model.calc_accel(s, speed, speed_lead,
                                                          accel_lead)

    def calc_speed(self, dt):
        for vehicle in self.vehicles.values():
            vehicle.speed = max(vehicle.speed + vehicle.accel * dt, 0)

    def calc_steering(self):
        for vehicle in self.vehicles.values():
            vehicle.calc_steering(self.pixel_width, self.pixel_height,
                                  0.0, self.calc_cross_track_error)

    def calc_cross_track_error(self, fx, fy, lane):
        lane_y = self.lane_center_lines[lane] * self.pixel_height
        return (0, fy - lane_y)
