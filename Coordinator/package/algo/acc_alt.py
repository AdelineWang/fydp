import math

class AccAlt:
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
        self.c = 0.99

    def calc_accel(self, gap, v, v_lead, a_lead):
        if gap < 0.001:
            return -self.max_decel

        T = self.desired_time_gap
        s0 = self.min_gap
        a = self.max_accel
        b = self.comfy_decel
        bmax = self.max_decel
        v0eff = min(self.desired_speed, self.speed_limit, self.max_speed)

        sstar = s0 + max(0, v*T + 0.5*v*(v - v_lead)/math.sqrt(a*b))
        gamma = sstar/gap
        if v < v0eff:
            acc_free = a*(1 - pow(v/v0eff, 4))
            if gamma >= 1:
                acc_IDM = acc_free*(1 - pow(gamma, 2))
            else:
                acc_IDM = acc_free*(1 - pow(gamma, 2*a/acc_free))
        else:
            acc_free = -b*(1 - pow(v0eff/v, a*4/b))
            if gamma >= 1:
                acc_IDM = acc_free + a*(1 - pow(gap, 2))
            else:
                acc_IDM = acc_free

        a_prime = min(a_lead, a)
        if v_lead*(v - v_lead) < -2*gap*a_prime:
            acc_CAH = pow(v, 2)*a_prime/(pow(v_lead, 2) - 2*gap*a_prime)
        else:
            acc_CAH = a_prime - pow(v - v_lead, 2)/(2*gap)*(1 if v > v_lead else 0)

        if acc_IDM >= acc_CAH:
            return acc_IDM
        else:
            acc_mix = (1 - self.c)*acc_IDM
            acc_mix += self.c*(acc_CAH + b*math.tanh((acc_IDM - acc_CAH)/b))
            return max(-bmax, acc_mix)
