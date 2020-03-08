from package.algo.acc import Acc

class Vehicle:
    """Represents an object on a road.

    Attributes:
        name: Internal identifier for the vehicle
        veh_id (str): ID for websocket communication
        length (float): Physical length in metres
        width (float): Physical width in metres
        lane (int): Lane index
        x, y (int): Pixel coordinates in image
        heading (float): Angle heading in degrees
        longitude (float): Physical distance along road in metres
        lattitude (float): Physical distance from lane center line in metres
        long_model: Model for vehicle behaviour along road
        steering (float): Steering angle in degrees
        speed (float): Speed in m/s
        accel (float): Acceleration in m/s^2
    """
    def __init__(self, name, veh_id, length, width, lane=0, x=0, y=0,
                 heading=0.0, longitude=0.0, latitude=0.0):
        self.name = name
        self.id = veh_id
        self.length = length
        self.width = width
        self.lane = lane
        self.x = x
        self.y = y
        self.heading = heading
        self.longitude = longitude
        self.latitude = latitude

        self.long_model = Acc(3, 3, 10, 1.4, 2, 1, 0.3, 0.5)
        self.steering = 0.0
        self.speed = 0.0
        self.accel = 0.0
