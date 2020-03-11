import numpy as np

# from package.algo.acc import Acc
from package.algo.acc_alt import AccAlt
from package.algo.mobil import Mobil
from package.algo.stanley import StanleyController

class Vehicle:
    """Represents an object on a road.

    Attributes:
        name: Internal identifier for the vehicle
        veh_id (str): ID for websocket communication
        length (float): Physical length [m]
        width (float): Physical width [m]
        axle_length (float): Wheel base length [m]
        max_steering (float): Max steering [rad]
        lane (int): Lane index
        x, y (int): Pixel coordinates in image
        heading (float): Angle heading [rad]
        longitude (float): Physical distance along road [m]
        lattitude (float): Physical distance from lane center line [m]
        long_model: Model for vehicle behaviour along road
        steer_model: Controller for steering angle
        steering (float): Steering angle [deg]
        speed (float): Speed [m/s]
        accel (float): Acceleration [m/s^2]
    """
    def __init__(self, name, veh_id, length=0.2, width=0.135, axle_length=0.14/2,
                 max_steering=np.radians(30.0), lane=0, x=0, y=0, heading=0.0,
                 longitude=0.0, latitude=0.0):
        self.name = name
        self.id = veh_id
        self.length = length
        self.width = width
        self.axle_length = axle_length
        self.max_steering = max_steering

        self.lane = lane
        self.x = x
        self.y = y
        self.heading = heading
        self.longitude = longitude
        self.latitude = latitude

        self.long_model = AccAlt(
            desired_speed=0.5,
            speed_limit=2,
            max_speed=2,
            desired_time_gap=0.5,
            min_gap=0.05,
            max_accel=0.2,
            comfy_decel=0.06,
            max_decel=0.2)
        self.lc_model = Mobil(b_safe=0.06, b_safe_max=0.2)
        self.steer_model = StanleyController(L=self.axle_length)

        self.steering = 0.0
        self.speed = 0.0
        self.accel = 0.0

        self.leader = None
        self.follower = None
        self.lane_change_requested = False
        self.lane_change_in_progress = False
        self.orig_lane = -1
        self.dest_lane = -1

    def calc_steering(self, pixel_width, pixel_height,desired_heading, error):
        cx = self.x * pixel_width
        cy = self.y * pixel_height
        delta = self.steer_model.calc(cx, cy, self.heading, self.speed,
                                      self.lane, desired_heading, error)
        self.steering = np.clip(delta, -self.max_steering, self.max_steering)

    def request_lane_change(self, target_lane):
        self.lane_change_requested = True
        self.orig_lane = self.lane
        self.dest_lane = target_lane

    def ack_lane_change(self):
        self.lane_change_in_progress = True

    def start_lane_change(self):
        self.lane = self.dest_lane

    def complete_lane_change(self):
        self.lane_change_requested = False
        self.lane_change_in_progress = False
        self.orig_lane = -1
        self.dest_lane = -1
