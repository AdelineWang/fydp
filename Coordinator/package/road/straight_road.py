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

        # Dictionary for roads
        self.vehicles = {}
        for vehicle in vehicles:
            self.vehicles[vehicle.name] = vehicle
    
    def update_positions(self):
        for vehicle in self.vehicles.values():
            vehicle.longitude = vehicle.x * self.pixel_width

            lane_center_line = self.lane_center_lines[vehicle.lane]
            latitude_pixel_delta = vehicle.y - lane_center_line
            vehicle.latitude = latitude_pixel_delta * self.pixel_width
            print(vehicle.name + ' (long, lat) = ' + str((vehicle.longitude, vehicle.latitude)))
