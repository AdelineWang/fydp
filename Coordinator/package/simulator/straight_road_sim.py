import keyboard

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.transforms import Affine2D

class StraightRoadSim:
    def __init__(self, calib, coord):
        self.xlim = calib.fov_width
        self.ylim = calib.fov_height
        self.coord = coord

    def run(self, dt):
        plt.figure(figsize=(8, 4.5))
        while True:
            if keyboard.is_pressed('q'):
                break
            elif keyboard.is_pressed('0'):
                self.coord.change_lane('green', 0)
            elif keyboard.is_pressed('1'):
                self.coord.change_lane('red', 1)

            plt.cla()
            plt.xlim(0, self.xlim)
            plt.ylim(self.ylim, 0)
            plt.gca().xaxis.tick_top()
            self.plot_lanes()
            self.plot_vehicles()
            plt.tight_layout()
            plt.pause(dt)

            self.coord.sim_update(dt)

    def plot_lanes(self):
        lanes = self.coord.road.lane_center_lines
        y_lane0 = self.coord.road.pixel_height * lanes[0]
        y_lane1 = self.coord.road.pixel_height * lanes[1]
        plt.axhline(y_lane0, color='grey', linestyle='-', zorder=1)
        plt.axhline(y_lane1, color='grey', linestyle='-', zorder=1)

    def plot_vehicles(self):
        pixel_width = self.coord.road.pixel_width
        pixel_height = self.coord.road.pixel_height
        ax = plt.gca()

        for veh in self.coord.road.vehicles.values():
            pos = [veh.x * pixel_width - veh.length / 2,
                   veh.y * pixel_height - veh.width / 2]

            ts = ax.transData
            coords = ts.transform(pos)
            tr = Affine2D().rotate_deg_around(coords[0], coords[1],
                                              np.rad2deg(-veh.heading))
            t = ts + tr

            rect = patches.Rectangle(pos, width=veh.length, height=veh.width,
                                     facecolor=veh.name, edgecolor=veh.name,
                                     zorder=2, transform=t)
            ax.add_patch(rect)
