import pygame as pg
import Colors

class TrafficLight:
    def __init__(self, width, height, radius, offset, longitude):
        self.width = width
        self.height = height
        self.radius = radius
        self.offset = offset
        self.longitude = longitude
        self.isGreen = True

        self.cx = 0
        self.cy = 0
        self.redCy = -offset
        self.greenCy = offset
        self.rect = (0, 0, 0, 0)

    def update(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.redCy = cy - self.radius - self.offset
        self.greenCy = cy + self.radius + self.offset
        self.rect = (cx - int(self.width/2), cy - (self.height/2),
                self.width, self.height)
    
    def toggle(self):
        self.isGreen = not self.isGreen
    
    def draw(self, surface):
        pg.draw.rect(surface, Colors.BLACK, self.rect)
        
        redColor = Colors.TL_RED_ON if not self.isGreen else Colors.TL_RED_OFF
        greenColor = Colors.TL_GREEN_ON if self.isGreen else Colors.TL_GREEN_OFF
        pg.draw.circle(surface, redColor, (self.cx, self.redCy), self.radius)
        pg.draw.circle(surface, greenColor, (self.cx, self.greenCy), self.radius)
