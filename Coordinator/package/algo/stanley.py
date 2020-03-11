import numpy as np

class StanleyController:
    """Steering controller

    Attributes:
        k (float): Controller gain
        L (float): Wheel base of vehicle [m]
    """
    def __init__(self, L, k=1):
        self.L = L
        self.k = k

    def calc(self, cx, cy, yaw, v, lane, desired_yaw, error):
        """Calculate steering angle.

        Args:
            cx (float): Vehicle center x-pos [m]
            cy (float): Vehicle center y-pos [m]
            yaw (float): Vehicle heading [rad]
            v (float): Current speed [m/s]
            lane (int): Current lane
            desired_yaw (float): Road heading [rad]
            error: Function to evaluate cross-track error (x, y)
        """
        # Calc front axle position
        fx = cx + self.L * np.cos(yaw)
        fy = cy + self.L * np.sin(yaw)
        dx, dy = error(fx, fy, lane)

        # Project RMS error onto front axle vector
        front_axle_vec = [-np.cos(yaw + np.pi / 2),
                        -np.sin(yaw + np.pi / 2)]
        error_front_axle = np.dot([dx, dy], front_axle_vec)

        # theta_e corrects the heading error
        theta_e = self.normalize_angle(desired_yaw - yaw)
        # theta_d corrects the cross track error
        theta_d = np.arctan2(self.k * error_front_axle, v)
        # Steering control
        delta = theta_e + theta_d

        return delta

    @staticmethod
    def normalize_angle(angle):
        """Normalize an angle to [-pi, pi]."""
        while angle > np.pi:
            angle -= 2.0 * np.pi

        while angle < -np.pi:
            angle += 2.0 * np.pi

        return angle
