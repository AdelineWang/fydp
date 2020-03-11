import math

class Acc:
    def __init__(self, desired_speed, speed_limit, max_speed,
                 desired_time_gap, min_gap, max_accel, comfy_decel, max_decel):
        self.desired_speed = desired_speed
        self.speed_limit = speed_limit
        self.max_speed = max_speed
        self.desired_time_gap = desired_time_gap
        self.min_gap = min_gap
        self.max_accel = max_accel
        self.comfy_decel = comfy_decel
        self.max_decel = max_decel
        self.cool = 0.99

    def calc_accel(self, gap, v, v_lead, a_lead):
        if gap < 0.001:
            return -self.max_decel

        T = self.desired_time_gap
        s0 = self.min_gap
        a = self.max_accel
        b = self.comfy_decel
        bmax = self.max_decel
        v0eff = min(self.desired_speed, self.speed_limit, self.max_speed)

        acc_free = a*(1 - pow(v/v0eff, 4)) if v < v0eff else a*(1 - v/v0eff)
        sstar = s0 + max(0, v*T + 0.5*v*(v - v_lead)/math.sqrt(a*b))
        acc_int = -a*pow(sstar/max(gap, s0), 2)
        acc_IDM = acc_free + acc_int

        acc_CAH = (v*v*a_lead/(v_lead*v_lead - 2*gap*a_lead)
            if (v_lead*(v - v_lead) < -2*gap*a_lead)
            else a_lead - pow(v - v_lead, 2)/(2 * max(gap, 0.01))*(1 if v > v_lead else 0))
        acc_CAH = min(acc_CAH, a)

        acc_mix = acc_IDM if acc_IDM > acc_CAH else acc_CAH + b*math.tanh((acc_IDM - acc_CAH)/b)
        acc_ACC = self.cool*acc_mix + (1 - self.cool)*acc_IDM
        return 0 if v0eff < 0.00001 else max(-bmax, acc_ACC)
