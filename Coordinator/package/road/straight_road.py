class StraightRoad:
    """Model for a straight road.

    Two lane road that is horizontal in the input image centered vertically.
    The lanes are offset from the center line by an amount specified.
    """
    def __init__(self, calib, lane_offset, vehicles):
        self.pixel_width, self.pixel_height = calib.calc_distance_per_pixel()

        # Road and lane locations
        self.center_line = calib.image_height / 2
        pixel_lane_offset = lane_offset / self.pixel_height
        lane0_center_line = self.center_line - pixel_lane_offset
        lane1_center_line = self.center_line + pixel_lane_offset
        self.lane_center_lines = [lane0_center_line, lane1_center_line]
        self.road_len = calib.fov_width

        # Dictionary for road objects
        self.vehicles = {}
        self.sorted_vehicles = [[], []]
        for vehicle in vehicles:
            self.vehicles[vehicle.name] = vehicle
            self.sorted_vehicles[vehicle.lane].append(vehicle.name)
        self.update_connections()

    def update_positions(self):
        """Update longitude and latitude values for all vehicles."""
        for veh in self.vehicles.values():
            veh.longitude = veh.x * self.pixel_width

            lane_center_line = self.lane_center_lines[veh.lane]
            latitude_pixel_delta = veh.y - lane_center_line
            veh.latitude = latitude_pixel_delta * self.pixel_width

    def update_connections(self):
        """Update vehicle chain for each lane."""
        for lane in range(len(self.sorted_vehicles)):
            # Sort vehicles in lane based on position in lane
            self.sorted_vehicles[lane].sort(
                key=lambda name: self.vehicles[name].longitude,
                reverse=True)

            # Update leaders and followers of all vehicles
            lane_vehicles = self.sorted_vehicles[lane]
            for (i, name) in enumerate(lane_vehicles):
                veh = self.vehicles[name]
                veh.leader = lane_vehicles[i - 1] if i > 0 else None
                if name != lane_vehicles[-1]:
                    veh.follower = lane_vehicles[i + 1]
                else:
                    veh.follower = None

        # Clean up leaders and followers of lane change vehicles
        for veh in self.vehicles.values():
            if not veh.lane_change_requested:
                continue

            orig_lane = self.sorted_vehicles[veh.orig_lane]
            orig_index = orig_lane.index(veh.name)
            orig_leader = orig_lane[orig_index - 1] if orig_index > 0 else None
            dest_lane = self.sorted_vehicles[veh.dest_lane]
            dest_index = dest_lane.index(veh.name)
            dest_leader = dest_lane[dest_index - 1] if dest_index > 0 else None

            if orig_leader is None:
                veh.leader = dest_leader
                continue
            elif dest_leader is None:
                vehe.leader = orig_leader
                continue
            orig_gap = self.vehicles[orig_leader].longitude - veh.long_model
            dest_gap = self.vehicles[dest_leader].longitude - veh.long_model
            veh.leader = orig_leader if orig_gap < dest_gap else dest_leader

            if veh.name != dest_lane[-1]:
                veh.follower = dest_lane[i + 1]
            else:
                veh.follower = None

    def update_lane_change(self):
        """Update lane change states."""
        for veh in self.vehicles.values():
            if not veh.lane_change_requested:
                continue

            if not veh.lane_change_in_progress:
                # Add vehicle to destination lane
                self.sorted_vehicles[veh.dest_lane].append(veh.name)
                veh.ack_lane_change()
                continue
            elif veh.lane == veh.dest_lane:
                if veh.latitude >= veh.width / 2:
                    continue

                veh.complete_lane_change()
                # Remove vehicle from original lane
                self.sorted_vehicles[veh.orig_lane].remove(veh.name)
                continue

            # Check if lane change is safe, then proceed
            lc_gap = veh.lc_gap
            if veh.leader is not None:
                leader = self.vehicles[veh.leader]
                safe_leader_gap = leader.longitude - veh.longitude > lc_gap
            else:
                safe_leader_gap = True

            if veh.follower is not None:
                follower = self.vehicles[veh.follower]
                safe_follower_gap = veh.longitude - follower.longitude > lc_gap
            else:
                safe_follower_gap = True

            if safe_leader_gap and safe_follower_gap:
                veh.start_lane_change()

    def calc_accel(self, dt):
        visited = set()
        for lane in range(len(self.sorted_vehicles)):
            for i, name in enumerate(self.sorted_vehicles[lane]):
                if name in visited:
                    continue
                visited.add(name)
                veh = self.vehicles[name]

                leader = veh.leader
                if leader is None:
                    veh.accel = self._calc_free_accel(veh)
                    continue

                veh_lead = self.vehicles[leader]
                veh.accel = self._calc_veh_accel(veh, veh_lead)

    def _calc_free_accel(self, veh):
        # Temporarily increase desired speed if vehicle merging behind
        if veh.follower is not None:
            veh_lag = self.vehicles[veh.follower]
            if veh_lag.is_performing_lane_change():
                force_speed = veh.long_model.effective_speed()*veh.lc_mult
                return veh.long_model.calc_accel(100, veh.speed, 0, 0,
                    force_desired_speed=force_speed)
        elif veh.is_performing_lane_change():
            force_speed = veh.long_model.effective_speed()*veh.lc_mult
            return veh.long_model.calc_accel(100, veh.speed, 0, 0,
                force_desired_speed=force_speed)

        return veh.long_model.calc_accel(100, veh.speed, 0, 0)

    def _calc_veh_accel(self, veh, veh_lead):
        s = veh_lead.longitude - veh.longitude
        speed = veh.speed
        speed_lead = veh_lead.speed
        accel_lead = veh_lead.accel

        # Match speed of leading vehicle while merging into lane. If gap is
        # less than safe gap, force slower desired speed
        if veh.is_performing_lane_change():
            force_speed = veh_lead.long_model.effective_speed()
            if s < veh.lc_gap:
                force_speed /= veh.lc_mult
            return veh.long_model.calc_accel(s, speed, speed_lead, accel_lead,
                                             force_desired_speed=force_speed)
        # Match speed of lane changing vehicle merging in front. If gap is
        # less than safe gap, force slower desired speed
        elif veh_lead.is_performing_lane_change():
            force_speed = veh_lead.long_model.effective_speed()
            if s < veh.lc_gap:
                force_speed /= veh.lc_mult
            return veh.long_model.calc_accel(s, speed, speed_lead, accel_lead,
                                             force_desired_speed=force_speed)

        return veh.long_model.calc_accel(s, speed, speed_lead, accel_lead)

    def calc_speed(self, dt):
        for vehicle in self.vehicles.values():
            vehicle.speed = max(vehicle.speed + vehicle.accel * dt, 0)

    def calc_steering(self):
        for vehicle in self.vehicles.values():
            vehicle.calc_steering(self.pixel_width, self.pixel_height,
                                  0.0, self.calc_cross_track_error)

    def calc_cross_track_error(self, fx, fy, lane):
        lane_y = self.lane_center_lines[lane] * self.pixel_height
        return (0, fy - lane_y)
