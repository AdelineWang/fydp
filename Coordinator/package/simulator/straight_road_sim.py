import matplotlib.pyplot as plt
import keyboard

class StraightRoadSim:
    def __init__(self, calib, coord):
        self.xlim = calib.fov_width
        self.ylim = calib.fov_height
        self.coord = coord

    def run(self, dt):
        pixel_width = self.coord.road.pixel_width
        pixel_height = self.coord.road.pixel_height

        while True:
            if (keyboard.is_pressed('q')):
                break

            plt.cla()
            plt.xlim(0, self.xlim)
            plt.ylim(self.ylim, 0)
            plt.gca().xaxis.tick_top()
            self.plot_lanes()
            for veh in self.coord.road.vehicles.values():
                plt.plot(veh.x * pixel_width, veh.y * pixel_height, marker='x',
                         color=veh.name, label=veh.name)
            plt.tight_layout()
            plt.pause(dt)

            self.coord.sim_update(dt)

    def plot_lanes(self):
        lanes = self.coord.road.lane_center_lines
        center_line = self.coord.road.center_line
        y_lane0 = self.coord.road.pixel_width * lanes[0]
        y_lane1 = self.coord.road.pixel_width * lanes[1]
        plt.axhline(y_lane0, color='b', linestyle='-')
        plt.axhline(y_lane1, color='b', linestyle='-')
