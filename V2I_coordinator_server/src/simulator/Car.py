import pygame as pg
from pygame.math import Vector2
from Acc import Acc

class Car:
    def __init__(self, image, longitude, lane, isTrafficLight):
        self.image = image
        self.speed = 0.0
        self.acceleration = 0.0
        self.steering = 30.0
        self.longitude = longitude
        self.lane = lane
        self.dvdt = 0.0

        self.isTrafficLight = isTrafficLight
        self.iLead = -100
        self.iLag = -100

        if isTrafficLight:
            self.longModel = Acc(0, 0, 0, 5, 5, 0, 10, 20)
        else:
            self.longModel = Acc(3, 3, 10, 1.4, 2, 1, 0.3, 0.5)

    def update(self, dt, roadLen):
        self.longitude += max(0,
                self.speed * dt + 0.5 * self.acceleration * dt * dt)
        self.speed = max(self.speed + self.acceleration * dt, 0)

        if self.longitude >= roadLen:
            self.longitude -= roadLen
    
    def draw(self, surface, cx, cy, angle):
        rotated = pg.transform.rotate(self.image, angle)
        rect = rotated.get_rect()
        surface.blit(rotated, Vector2(cx, cy) - (rect.width/2, rect.height/2))
