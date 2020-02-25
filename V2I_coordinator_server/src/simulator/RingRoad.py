import pygame as pg
import math
import Colors
from Car import Car

class RingRoad:
    def __init__(self, cx, cy, radius, physicalScale, numLanes = 1, laneWidth = 40):
        self.physicalScale = physicalScale
        self.radius = radius
        self.center = (cx, cy)
        self.numLanes = numLanes
        self.laneWidth = laneWidth

        self.roadLength = 2 * math.pi * radius * physicalScale
        self.radiusPhys = radius * physicalScale
        self.centerPhys = (cx * physicalScale, cy * physicalScale)
        self.laneWidthPhys = laneWidth * physicalScale

        self.vehicles = []
    
    def updateConnections(self):
        n = len(self.vehicles)
        for (i, veh) in enumerate(self.vehicles):
            veh.iLead = n - 1 if i == 0 else i - 1 
            veh.iLag = 0 if i == n - 1 else i + 1
    
    def sortVehicles(self):
        self.vehicles.sort(key=lambda veh: veh.longitude, reverse=True)

    def calculateAccel(self, veh, light, dt):
        for (i, veh) in enumerate(self.vehicles):
            speed = veh.speed
            iLead = veh.iLead
            vehLead = self.vehicles[iLead]
            s = vehLead.longitude - veh.longitude
            speedLead = vehLead.speed
            accLead = vehLead.acceleration

            # Vehicle i is leader in ring
            if iLead >= i:
                s += self.roadLength
            
            if not veh.isTrafficLight:
                veh.acceleration = veh.longModel.calcAccel(s, speed, speedLead, accLead)
            else:
                veh.acceleration = 0

        # veh.speed = 5
        # veh.longitude += veh.speed * dt
        # if veh.longitude >= self.roadLength:
        #     veh.longitude -= self.roadLength
    
    def updateSpeedPosition(self, car, dt):
        car.update(dt, self.roadLength)
        self.sortVehicles()
        self.updateConnections()
    
    def toggleTrafficLight(self, light, car):
        light.toggle()
        if light.isGreen:
            self.vehicles = [car]
        else:
            lightVehicle = Car(None, 0.0, 2, True)
            self.vehicles.append(lightVehicle)
            self.sortVehicles()
        self.updateConnections()
    
    def trajectoryX(self, longitude):
        return self.centerPhys[0] + self.radiusPhys * math.sin(longitude / self.radiusPhys)

    def trajectoryY(self, longitude):
        return self.centerPhys[1] + self.radiusPhys * math.cos(longitude / self.radiusPhys)
    
    def getPhi(self, longitude):
        smallVal = 0.0000001
        du = 0.1
        uLoc = max(du, min(self.roadLength - du, longitude))
        u1 = uLoc + du
        u2 = uLoc - du
        dx = self.trajectoryX(u1) - self.trajectoryX(u2)
        dy = self.trajectoryY(u1) - self.trajectoryY(u2)

        if abs(dx) < smallVal and abs(dy) < smallVal:
            raise Exception("Can't compute phi for same point!")

        phi = 0.5 * math.pi if abs(dx) < smallVal else math.atan(dy/dx)
        if dx < 0 or (abs(dx) < smallVal and dy < 0):
            phi += math.pi

        return phi
    
    def drawVehicle(self, surface, veh):
        phiRoad = self.getPhi(veh.longitude)
        # phiVehRel = -math.atan(veh.dvdt * self.laneWidthPhys / veh.speed) 
        # phiVeh = phiRoad + phiVehRel
        phiVeh = phiRoad + math.pi / 2

        uCenterPhys = veh.longitude
        vCenterPhys = self.laneWidthPhys * veh.lane + self.laneWidthPhys * 0.5

        cosPhiRoad = math.cos(phiRoad)
        sinPhiRoad = math.sin(phiRoad)

        cx = (self.trajectoryX(uCenterPhys)
                + vCenterPhys * sinPhiRoad) / self.physicalScale
        cy = (self.trajectoryY(uCenterPhys)
                - vCenterPhys * cosPhiRoad) / self.physicalScale
        veh.draw(surface, cx, cy, -math.degrees(phiVeh))

        font = pg.font.Font(None, 30)
        longitudeText = font.render(str(veh.longitude), True, Colors.WHITE)
        phiRoadText = font.render(str(phiRoad), True, Colors.WHITE)
        speedText = font.render(str(veh.speed), True, Colors.WHITE)
        accelText = font.render(str(veh.acceleration), True, Colors.WHITE)
        surface.blit(longitudeText, (800, 10))
        surface.blit(phiRoadText, (800, 50))
        surface.blit(speedText, (800, 90))
        surface.blit(accelText, (800, 130))
    
    def placeLight(self, light):
        phiRoad = self.getPhi(light.longitude)
        uCenterPhys = light.longitude
        vCenterPhys = self.laneWidthPhys * (self.numLanes + 1)

        cosPhiRoad = math.cos(phiRoad)
        sinPhiRoad = math.sin(phiRoad)

        cx = (self.trajectoryX(uCenterPhys)
                + vCenterPhys * sinPhiRoad) / self.physicalScale
        cy = (self.trajectoryY(uCenterPhys)
                - vCenterPhys * cosPhiRoad) / self.physicalScale
        light.update(int(cx), int(cy))

    def draw(self, surface):
        roadWidth = self.numLanes * self.laneWidth
        pg.draw.circle(surface, Colors.ASPHALT, self.center, self.radius, roadWidth)

        for i in range(1, self.numLanes):
            laneDividerRadius = self.radius - i * self.laneWidth
            pg.draw.circle(surface, Colors.WHITE, self.center, laneDividerRadius, 1)
