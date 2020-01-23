from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.sensor import INPUT_1, INPUT_2
from odometrium.main import Odometrium


class LegoRobot:
    def __init__(self):
        self.color_sensor = ColorSensor()
        self.touch_sensor1 = TouchSensor(INPUT_1)
        self.touch_sensor2 = TouchSensor(INPUT_2)
        self.odo = Odometrium(left='B', right='C', wheel_diameter=5.5, wheel_distance=12, count_per_rot_left=None,
                              count_per_rot_right=None, debug=False, curve_adjustment=1)

    def move_forward(self, speed, time):
        self.odo.move(speed, speed, time)

    def rotate_right(self, speed, time):
        self.odo.move(speed, -speed, time)

    def rotate_left(self, speed, time):
        self.odo.move(-speed, speed, time)

    def move_backward(self, speed, time):
        self.odo.move(-speed, -speed, time)

    def stop(self):
        self.odo.stop()

    def color(self):
        return self.color_sensor.reflected_light_intensity

    def touch_right(self):
        return self.touch_sensor1.is_pressed

    def touch_left(self):
        return self.touch_sensor2.is_pressed

    def position(self):
        return [self.odo.x, self.odo.y]
