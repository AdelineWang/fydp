import math

class Acc:
    def __init__(self, desiredSpeed, speedLimit, maxSpeed, desiredTimeGap,
            minGap, maxAccel, comfyDecel, maxDecel):
        self.desiredSpeed = desiredSpeed
        self.speedLimit = speedLimit
        self.maxSpeed = maxSpeed
        self.desiredTimeGap = desiredTimeGap
        self.minGap = minGap
        self.maxAccel = maxAccel
        self.comfyDecel = comfyDecel
        self.maxDecel = maxDecel
        self.cool = 0.99

    def calc_accel(self, gap, v, vLead, aLead):
        if gap < 0.001:
            return -self.maxDecel
        
        T = self.desiredTimeGap
        s0 = self.minGap
        a = self.maxAccel
        b = self.comfyDecel
        bmax = self.maxDecel
        
        v0eff = min(self.desiredSpeed, self.speedLimit, self.maxSpeed)
        accFree = a*(1 - pow(v/v0eff, 4)) if v < v0eff else a*(1 - v/v0eff)
        sstar = s0 + max(0, v*T + 0.5*v*(v - vLead)/math.sqrt(a*b))
        accInt = -a*pow(sstar/max(gap, s0), 2)
        accIDM = accFree + accInt

        accCAH = (v*v*aLead/(vLead*vLead - 2*gap*aLead)
                if (vLead*(v - vLead) < -2*gap*aLead)
                else aLead - pow(v - vLead, 2)/(2 * max(gap, 0.01))*(1 if v > vLead else 0))
        accCAH = min(accCAH, a)

        accMix = accIDM if accIDM > accCAH else accCAH + b*math.tanh((accIDM - accCAH)/b)
        accACC = self.cool*accMix + (1 - self.cool)*accIDM
        accReturn = 0 if v0eff < 0.00001 else max(-bmax, accACC) 
        return accReturn
