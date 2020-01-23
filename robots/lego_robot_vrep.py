from pyvrep import VRep
import time


class LegoRobot:

    def __init__(self, api: VRep):
        self._api = api
        self._left_motor = api.joint.with_velocity_control("left_motor")
        self._right_motor = api.joint.with_velocity_control("right_motor")
        self._ultrasonic_sensor = api.sensor.proximity("ultrasonic_sensor")
        self._color_sensor = api.sensor.vision("color_sensor")
        self._touch_sensor_right = api.sensor.touch("touch_button_right")
        self._touch_sensor_left = api.sensor.touch("touch_button_left")
        self._tracer = api.sensor.position("LineTracer")

    def rotate_right(self, speed=2.0):
        self._set_two_motor(speed, -speed)
   
    def rotate_left(self, speed=2.0):
        self._set_two_motor(-speed, speed)

    def move_forward(self, speed=2.0):
        self._set_two_motor(speed, speed)

    def move_backward(self, speed=2.0):
        self._set_two_motor(-speed, -speed)

    def _set_two_motor(self, left: float, right: float):
        self._left_motor.set_target_velocity(left)
        self._right_motor.set_target_velocity(right)

    def stop(self):
        self._set_two_motor(0, 0)

    def color(self) -> int:
        image = self._color_sensor.raw_image(is_grey_scale=True)
        average = sum(image) / len(image)
        return average

    def touch_right(self):
        return self._touch_sensor_right.get_state()

    def touch_left(self):
        return self._touch_sensor_left.get_state()

    def ultrasonic(self):
        return self._ultrasonic_sensor.read()[1].distance()

    def position(self):
        return self._tracer.get_position()

    def angle(self):
        return self._tracer.get_orientation()



