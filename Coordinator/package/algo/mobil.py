class Mobil:
    """Lane changing model

    Attributes:
        b_safe (float): safe deceleration at max speed [m/s^2]
        b_safe_max (float): safe deceleration at speed zero [m/s^2]
        p (float): politeness factor
        b_thr (float): lane-changing threshold [m/s^2]
        b_bias_right (float): bias right [m/s^2]
    """
    def __init__(self, b_safe, b_safe_max, p=0.0, b_thr=0.0, b_bias_right=0.0):
        self.b_safe = b_safe
        self.b_safe_max = b_safe_max
        self.p = p
        self.b_thr = b_thr
        self.b_bias_right = b_bias_right

    def eval_lane_change(self, v_rel, acc, acc_new, acc_lag_new, to_right):
        """Return whether immediate lane change is safe and desired

        vrel (float): v/v0; increase b_safe with decreaseing v_rel
        acc (float): own acceleration at old lane
        acc_new (float): prospective own acceleration at new lane
        acc_lag_new (float): prospective acceleration of new leader
        to_right (bool): direction of lane change
        """
        sign_right = 1 if to_right else -1
        # Hard-prohibit lane change against bias if |bias| > 9 m/s^2
        if (self.b_bias_right*sign_right < -9):
            return False

        # Safety criterion
        b_safe_actual = v_rel*self.b_safe + (1 - v_rel)*self.b_safe_max
        if sign_right*self.b_bias_right > 40:
            return True
        if acc_lag_new < min(-b_safe_actual, -abs(self.b_bias_right)):
            return False

        # Incentive criterion
        dacc = acc_new - acc + self.p*acc_lag_new \
            + self.b_bias_right*sign_right + self.b_thr

        return (dacc > 0)
