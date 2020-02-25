import os
import pygame as pg
import json
import websocket

import Colors
from RingRoad import RingRoad
from Car import Car
from TrafficLight import TrafficLight

class Simulation:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Traffic State Simulation")
        self.size = (1024, 720)
        self.screen = pg.display.set_mode(self.size)
        self.font = pg.font.Font(None, 30)
        self.clock = pg.time.Clock()
        self.exit = False

    def run(self):
        carImage = self.loadCarImage()
        road = RingRoad(360, 360, 320, 0.05, 3, 40)
        car = Car(carImage, 0.0, 2, False)
        light = TrafficLight(60, 120, 20, 5, 0)
        road.placeLight(light)

        road.vehicles.append(car)
        road.sortVehicles()
        road.updateConnections()

        LIGHTS_EVENT = pg.USEREVENT + 1
        UPDATE_EVENT = pg.USEREVENT + 2
        pg.time.set_timer(LIGHTS_EVENT, 10000)
        pg.time.set_timer(UPDATE_EVENT, 5)

        while not self.exit:
            dt = self.clock.get_time() / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.exit = True
                elif event.type == LIGHTS_EVENT:
                    road.toggleTrafficLight(light, car)
                elif event.type == UPDATE_EVENT:
                    wsAddr = "ws://10.36.79.240:8080"
                    ws = websocket.create_connection(wsAddr)
                    ws.send(json.dumps({
                        "id": -2,
                        "vehId": 1732122,
                        "type": "drive",
                        "speed": car.speed,
                        "steering": car.steering
                    }))
                    ws.close()

            road.calculateAccel(car, light, dt)
            road.updateSpeedPosition(car, dt)
            
            self.screen.fill(Colors.GRASS)
            road.draw(self.screen)
            road.drawVehicle(self.screen, car)
            light.draw(self.screen)

            fps = self.font.render(str(int(self.clock.get_fps())+100), True, Colors.WHITE)
            self.screen.blit(fps, (10, 10))

            pg.display.flip()
            self.clock.tick()

        pg.quit()
    
    def loadCarImage(self):
        currDir = os.path.dirname(os.path.abspath(__file__))
        carImagePath = os.path.join(currDir, "pixel_car.png")
        carImage = pg.image.load(carImagePath)
        carImage = pg.transform.scale(carImage, (40, 72))
        carImage = pg.transform.rotate(carImage, 180)
        return carImage

if __name__ == "__main__":
    sim = Simulation()
    sim.run()
