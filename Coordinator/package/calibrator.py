class Calibrator:
    def __init__(self, image_width, image_height, camera_height):
        """Initializes critical calibration values.

        The Logitech C920 webcam has 1920x1080 and 1280x720 resolutions.
        (360p, 480p, 720p, 1080p)
        Image width and height in pixel count. Camera height in meters.
        """
        self.image_width = image_width
        self.image_height = image_height
        self.camera_height = camera_height
        self.fov_width = None
        self.fov_height = None

    def calibrate_alt(self, calib_camera_height, calib_fov_width,
                      calib_fov_height):
        """Calibrate using scaled FOV values from a different camera height.

        Measure the camera FOV width and height at a low camera height. The FOV
        values for the final camera height is given by similar triangles (i.e.
        scaling the calibration values proportionally).
        """
        self.calib_camera_height = calib_camera_height
        self.calib_camera_fov_width = calib_fov_width
        self.calib_camera_fov_height = calib_fov_height

        width_scaling = calib_fov_width / calib_camera_height
        self.fov_width = width_scaling * self.camera_height

        height_scaling = calib_fov_height / calib_camera_height
        self.fov_height = height_scaling * self.camera_height

    def calibrate(self, fov_width, fov_height):
        """Calibrate using final camera height values."""
        self.fov_width = fov_width
        self.fov_height = fov_height

    def calc_distance_per_pixel(self):
        """Returns the width and height mapping of a pixel."""
        width_per_pixel = self.fov_width / self.image_width
        height_per_pixel = self.fov_height / self.image_height
        return width_per_pixel, height_per_pixel

    def calc_error_per_pixel(self, veh_height):
        """Returns the max error from the current setup."""
        width_error, height_error = self.calc_distance_per_pixel()

        width_scaling = self.fov_width / self.camera_height
        veh_width_error = width_scaling * veh_height

        height_scaling = self.fov_height / self.camera_height
        veh_height_error = height_scaling * veh_height

        return width_error + veh_width_error, height_error + veh_height_error
