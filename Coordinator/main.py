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

    # Camera at 1280x720 image resolution mounted 2m high
    calib = Calibrator(1280, 720, 2.0)
    # Calibrated at 0.65m high, covers 0.9m by 0.4m area
    calib.calibrate_alt(0.65, 0.9, 0.4)
    print(f'(width, height) = ({calib.fov_width}, {calib.fov_height})')
    print('(width, height) per pix = ' + str(calib.calc_distance_per_pixel()))
    print('(error_width, error_height) = ' + str(calib.calc_error_per_pixel(0.05)))

    red_vehicle = Vehicle('red', '177130', x=50, y=calib.image_height/2 - 60, lane=0)
    blue_vehicle = Vehicle('blue', '132829', y=calib.image_height/2 + 30, lane=1)
    green_vehicle = Vehicle('green', '100202', x=100, y=calib.image_height/2 + 80, lane=1)
    vehicles = [red_vehicle, blue_vehicle, green_vehicle]

    road = StraightRoad(calib, 0.1, vehicles)
    processor = ImageProcessor()
    coord = Coordinator(road, processor)
    if is_simulation:
        sim = StraightRoadSim(calib, coord)
        sim.run(0.1)
    else:
        coord.update()
