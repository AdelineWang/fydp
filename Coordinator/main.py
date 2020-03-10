#!/usr/bin/env python3

if __name__ == '__main__':
    import sys

    from package.image_processor import ImageProcessor
    from package.coordinator import Coordinator
    from package.calibrator import Calibrator
    from package.road.vehicle import Vehicle
    from package.road.straight_road import StraightRoad
    from package.simulator.straight_road_sim import StraightRoadSim

    road_type = 'straight'
    is_simulation = False
    for i, arg in enumerate(sys.argv):
        print(f'Argument {i}: {arg}')
        if i == 1:
            road_type = arg
        elif i == 2 and arg == 'sim':
            is_simulation = True

    # Fake calibration data
    # Camera at 1280x720 image resolution mounted 2m high
    calib = Calibrator(1280, 720, 2.0)
    # Calibrated at 0.3m high, covers 0.5m by 0.281 area
    calib.calibrate_alt(0.3, 0.42, 0.236)
    print('(width, height) per pix = ' + str(calib.calc_distance_per_pixel()))
    print('(error_width, error_height) = ' + str(calib.calc_error_per_pixel(0.05)))

    red_vehicle = Vehicle('red', '177130', 0.15, 0.5, y=calib.image_height/2 - 20, lane=1)
    blue_vehicle = Vehicle('blue', '132829', 0.15, 0.5, y=calib.image_height/2 + 15)
    green_vehicle = Vehicle('green', '100202', 0.15, 0.5, x=100, y=calib.image_height/2 + 40)
    vehicles = [red_vehicle, blue_vehicle, green_vehicle]

    road = StraightRoad(calib, 0.06, vehicles)
    processor = ImageProcessor()
    coord = Coordinator(road, processor)
    if is_simulation:
        sim = StraightRoadSim(calib, coord)
        sim.run(0.1)
    else:
        coord.update()
