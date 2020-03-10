#!/usr/bin/env python3

if __name__ == '__main__':
    from package.processor import ImageProcessor
    from package.coordinator import Coordinator
    from package.calibrator import Calibrator
    from package.road.vehicle import Vehicle
    from package.road.straight_road import StraightRoad

    # Fake calibration data
    # Camera at 1280x720 image resolution mounted 2m high
    calib = Calibrator(1280, 720, 2.0)
    # Calibrated at 0.3m high, covers 0.5m by 0.281 area
    calib.calibrate_alt(0.3, 0.42, 0.236)
    print('(width, height) per pix = ' + str(calib.calc_distance_per_pixel()))
    print('(error_width, error_height) = ' + str(calib.calc_error_per_pixel(0.05)))

    red_vehicle = Vehicle('red', '177130', 0.15, 0.5)
    blue_vehicle = Vehicle('blue', '132829', 0.15, 0.5)
    green_vehicle = Vehicle('green', '100202', 0.15, 0.5)
    vehicles = [red_vehicle, blue_vehicle, green_vehicle]

    road = StraightRoad(calib, 0.06, vehicles)
    processor = ImageProcessor()
    coord = Coordinator(road, processor)
    coord.update()
