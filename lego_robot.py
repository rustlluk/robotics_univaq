from pyvrep import VRep
import time


class LegoRobot:

    def __init__(self, api: VRep):
        self._api = api
        self._left_motor = api.joint.with_velocity_control("left_motor")
        self._right_motor = api.joint.with_velocity_control("right_motor")
        #self._left_sensor = api.sensor.proximity("Pioneer_p3dx_ultrasonicSensor3")
        #self._right_sensor = api.sensor.proximity("Pioneer_p3dx_ultrasonicSensor6")
        self._color_sensor = api.sensor.vision("color_sensor")
        self._touch_sensor_right = api.sensor.touch("touch_button_right")
        self._touch_sensor_left = api.sensor.touch("touch_button_left")

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

    def color(self) -> int:
        image = self._color_sensor.raw_image(is_grey_scale=True)
        average = sum(image) / len(image)
        return average

    def touch_right(self):
        return self._touch_sensor_right.get_state()

    def touch_left(self):
        return self._touch_sensor_left.get_state()

    #def right_length(self):
        #return self._right_sensor.read()[1].distance()

    #def left_length(self):
        #return self._left_sensor.read()[1].distance()

with VRep.connect("127.0.0.1", 19997) as api:
    #api.simulation.start()
    r = LegoRobot(api)

    #r.move_forward()
    follow = False
    while True:
        print('right',r.touch_right(),'left',r.touch_left())
        """
        if follow == True:
            if r.color()==5:
                r.rotate_right()
            elif r.color()==-1:
                r.rotate_left()
            time.sleep(0.05)
            r.move_forward()
            time.sleep(0.05)
        else:
            if r.color()==5:
                follow = True
        """
        #print(r.touch())
#api.simulation.stop()



