import queue
from multiprocessing import Process
from threading import Thread
import time
from Adafruit_MotorHAT import Adafruit_MotorHAT

from duckietown_slimremote.helpers import get_right_queue
from duckietown_slimremote.robot.constants import MOTOR_MAX_SPEED, DECELERATION_TIMEOUT, DECELERATION_BREAK_TIME, \
    DECELERATION_STEPS

from queue import Queue

from duckietown_slimremote.robot.led import RGB_LED


def denormalize_speed(norm):
    unshifted = (norm + 1) / 2
    # now it's in [0;1]
    denorm = unshifted * MOTOR_MAX_SPEED * 2 - MOTOR_MAX_SPEED
    # this it's in [-MOTOR_MAX_SPEED;MOTOR_MAX_SPEED]
    return int(round(denorm))


def normalize_speed(denorm):
    norm = (float(denorm) + MOTOR_MAX_SPEED) / (MOTOR_MAX_SPEED * 2)
    # now it's in [0;1]
    shifted = norm * 2 - 1
    # now it's in [-1;1]
    return shifted


def _inverse_kinematics(v, omega):
    # TODO

    # very shitty temporary solution
    v_left = v
    v_right = omega
    return (v_left, v_right)


def _clip_normalized_speed(speed):
    _speed = float(speed)
    return max(min(_speed, 1), -1)


def _prep_action(speed):
    _speed = _clip_normalized_speed(speed)
    # print("speed clipped", _speed)
    _denorm = denormalize_speed(_speed)
    # print("speed denormalized", _denorm)

    direction = Adafruit_MotorHAT.BACKWARD  # is forward
    if _denorm < 0:
        _denorm *= -1
        direction = Adafruit_MotorHAT.FORWARD
    elif _denorm == 0:
        direction = Adafruit_MotorHAT.RELEASE

    action = {"speed": _denorm, "direction": direction}
    # print("action:", action)

    return action


def ease_out_quad(time_in_animation, start_value, value_change, duration):
    """ easing function from http://www.gizma.com/easing/
    """

    time_in_animation /= duration
    return -value_change * time_in_animation * (time_in_animation - 2) + start_value


def ease_out_action(last_action, delta):
    new_action = [
        ease_out_quad(delta, last_action[0], -last_action[0], DECELERATION_BREAK_TIME),
        ease_out_quad(delta, last_action[1], -last_action[1], DECELERATION_BREAK_TIME)
    ]
    return new_action


class Controller():
    def __init__(self, with_rgb=True):
        self.with_rgb = with_rgb

        motorhat = Adafruit_MotorHAT(addr=0x60)
        self.leftMotor = motorhat.getMotor(1)
        self.rightMotor = motorhat.getMotor(2)

        if self.with_rgb:
            self.rgb = RGB_LED()

    def left_action(self, speed):
        """ set the speed and direction of the left wheel (negative = backwards)

        :param speed: scalar float in range [-1;1]
        :return: None
        """

        action = _prep_action(speed)
        self.leftMotor.setSpeed(action["speed"])
        self.leftMotor.run(action["direction"])

    def right_action(self, speed):
        """ set the speed and direction of the left wheel (negative = backwards)

        :param speed: scalar float in range [-1;1]
        :return: None
        """

        action = _prep_action(speed)
        self.rightMotor.setSpeed(action["speed"])
        self.rightMotor.run(action["direction"])

    def wheel_action(self, motor, speed):
        assert motor in ["left", "right"]

        if motor == "left":
            self.left_action(speed)
        else:
            self.right_action(speed)

    def list_action(self, speeds):
        """ set speeds of right and left motor in that order

        :param speeds: list or numpy array with two floats in [-1;1]
        :return: None
        """

        assert len(speeds) == 2
        self.right_action(speeds[0])
        self.left_action(speeds[1])

    def rgb_action(self, rgb):
        assert len(rgb) == 3
        assert max(rgb) <= 1 and min(rgb) >= 0

        for led in range(5):
            self.rgb.setRGB(led, rgb)

    def rgb_off(self):
        self.rgb_action([0] * 3)

    def stop(self):
        self.list_action([0, 0])

    def ik_action(self, v, omega):
        ik = _inverse_kinematics(v, omega)
        self.list_action(ik)
        return ik


def make_async_controller(base):
    """ allows to instantiate the motor controller as thread or as process

    :param base: options are Thread|Process
    :return:
    """

    class AsyncController(base):
        def __init__(self, queue):
            super(AsyncController, self).__init__()
            self.queue = queue
            self.robot = Controller()
            self.last_action_time = time.time()
            self.last_action = []

        def run(self):
            keep_running = True
            while keep_running:
                if not self.queue.empty():
                    action = self.queue.get()

                    if action == "quit":
                        keep_running = False
                        self.robot.list_action([0, 0])
                        self.robot.rgb_off()
                    else:
                        ik = self.robot.ik_action(action[:2])
                        if len(action) == 5:
                            self.robot.rgb_action(action[2:])

                        self.last_action_time = time.time()
                        self.last_action = ik

                else:
                    # check if it's time to break
                    delta = time.time() - self.last_action_time - DECELERATION_TIMEOUT

                    if delta >= 0 and delta < DECELERATION_BREAK_TIME:
                        # decelerate
                        if len(self.last_action) == 2:
                            new_action = ease_out_action(self.last_action, delta)
                            self.robot.list_action(new_action)

                            time.sleep(1 / DECELERATION_STEPS)
                    elif delta >= DECELERATION_BREAK_TIME and len(self.last_action) == 2:
                        # this is run only once after decel to
                        # make sure the robot comes to a full stop
                        # and doesn't continue to move at 0.00001 speed
                        self.last_action = []
                        self.robot.stop()

    queue = get_right_queue(base)

    return AsyncController, queue


class FailsafeController():
    ''' Main class for controlling the robot.
    Includes automatic deceleration if no action
    is received for DECELERATION_TIMEOUT

    '''

    def __init__(self):
        ctrl_class, ctrl_queue = make_async_controller(Process)
        self.queue = ctrl_queue(2)

        self.ctrl = ctrl_class(self.queue)
        self.ctrl.daemon = True
        self.ctrl.start()

    def run(self, action):
        # action must be either a list, tuple or NumPy array of len 2
        assert len(action) == 2 or len(action) == 5
        if not self.queue.empty():
            try:
                self.queue.get(timeout=0.02)
            except queue.Empty:  # this is independent of queue type
                pass  # this happens sometimes, no bad consequence

        self.queue.put(action)
        time.sleep(0.01)  # this is to block flooding

    def stop(self):
        self.queue.put("quit")
        self.ctrl.join()


if __name__ == '__main__':
    # TEST
    import time


    def test_simple_control():

        import numpy as np

        print("testing motor controller")

        ctrl = Controller()

        print("forward slow")
        ctrl.left_action(0.5)
        ctrl.right_action(0.5)

        time.sleep(1)

        print("spin fast")
        ctrl.wheel_action("left", 5)  # should clip to 1
        ctrl.wheel_action("right", -10)  # should clip to -1

        time.sleep(1)

        print("back slow")

        ctrl.list_action(np.array([-0.5, -0.5]))

        time.sleep(1)

        print("done")
        ctrl.stop()


    def test_failsafe():
        print("testing failsafe mode")

        ctrl = FailsafeController()
        print("started robot, sending action, then sleeping for 1s")
        ctrl.run((0.7, 0.7))
        time.sleep(2)

        print("robot should have halted by now...")
        time.sleep(2)
        print("sending constant motor commands to keep it going")

        for i in range(100):
            ctrl.run((1, -1))
            time.sleep(1 / 50)

        print("now decelerating")
        time.sleep(2)

        print("now sending move commands that are slightly too late, "
              "so should decelerate ever so slightly")

        for i in range(3):
            ctrl.run((-1, 1))
            time.sleep(1.2)

        print("done")
        ctrl.stop()


    test_failsafe()


    def stop():
        ctrl = Controller()
        ctrl.stop()

    # stop()
