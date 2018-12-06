# The gamepad/"joystick"-related stuff in here is mostly from https://gist.github.com/rdb/8864666. Huge thanks to @rdb

import queue
import time # don't remove this
from multiprocessing import Process
import numpy as np
from Adafruit_MotorHAT import Adafruit_MotorHAT
import os, struct, array
from fcntl import ioctl

from duckietown_slimremote.helpers import get_right_queue
from duckietown_slimremote.robot.constants import MOTOR_MAX_SPEED, DECELERATION_TIMEOUT, DECELERATION_BREAK_TIME, \
    DECELERATION_STEPS, JOYSTICK_PATH, CHECK_JOYSTICK_EVERY_N, JOYSTICK_AXIS_NAMES, JOYSTICK_BUTTON_NAMES, IK
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


class Controller:
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
        # print ("speed left/right: {}|{}".format(speeds[0],speeds[1]))
        self.right_action(speeds[0])
        self.left_action(speeds[1])
        return speeds

    def rgb_action(self, rgb):
        assert len(rgb) == 3
        assert max(rgb) <= 1 and min(rgb) >= 0

        for led in range(5):
            self.rgb.setRGB(led, rgb)

    def rgb_off(self):
        self.rgb_action([0] * 3)

    def stop(self):
        self.list_action([0, 0])


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

            self.joystick = None
            self.button_map = []
            self.button_states = {}
            self.axis_map = []
            self.axis_states = {}
            self.halt = False
            self.joystick_cmd = np.zeros(2,dtype=np.float32)

        def get_button_map(self):
            buf = array.array('B', [0])
            ioctl(self.joystick, 0x80016a12, buf)  # JSIOCGBUTTONS
            num_buttons = buf[0]

            buf = array.array('H', [0] * 200)
            ioctl(self.joystick, 0x80406a34, buf)  # JSIOCGBTNMAP

            for btn in buf[:num_buttons]:
                btn_name = JOYSTICK_BUTTON_NAMES.get(btn, 'unknown(0x%03x)' % btn)
                self.button_map.append(btn_name)
                self.button_states[btn_name] = 0

        def get_axis_map(self):
            buf = array.array('B', [0])
            ioctl(self.joystick, 0x80016a11, buf)  # JSIOCGAXES
            num_axes = buf[0]

            buf = array.array('B', [0] * 0x40)
            ioctl(self.joystick, 0x80406a32, buf)  # JSIOCGAXMAP

            for axis in buf[:num_axes]:
                axis_name = JOYSTICK_AXIS_NAMES.get(axis, 'unknown(0x%02x)' % axis)
                self.axis_map.append(axis_name)
                self.axis_states[axis_name] = 0.0

        def ik(self):
            vel = self.axis_states["y"]
            angle = - self.axis_states["x"]
            k_r = IK["k"]
            k_l = IK["k"]

            k_r_inv = (IK["gain"] + IK["trim"]) / k_r
            k_l_inv = (IK["gain"] - IK["trim"]) / k_l

            omega_r = (vel + 0.5 * angle * IK["wheel_dist"]) / IK["radius"]
            omega_l = (vel - 0.5 * angle * IK["wheel_dist"]) / IK["radius"]

            out = [omega_l * k_l_inv, omega_r * k_r_inv]
            self.joystick_cmd = np.clip(out, -IK["limit"], IK["limit"])

            # cutoff if joystick near resting position
            if (np.abs(self.joystick_cmd) < IK["epsilon"]).all():
                self.joystick_cmd[0] = 0
                self.joystick_cmd[1] = 0


        def handle_joystick(self):
            try:
                evbuf = os.read(self.joystick, 8)
                if evbuf:
                    time, value, type, number = struct.unpack('IhBB', evbuf)
                    if type & 0x80:
                        pass  # init

                    if type & 0x01:
                        button = self.button_map[number]
                        if button:
                            self.button_states[button] = value
                            # if value:
                            #     print("{} pressed".format(button))
                            # else:
                            #     print("{} released".format(button))
                            if button == "mode" and value:
                                self.halt = not self.halt
                                if self.halt:
                                    print("=== HALT ===")
                                else:
                                    print("=== UN-HALT ===")

                    if type & 0x02:
                        axis = self.axis_map[number]
                        if axis:
                            fvalue = value / 32767.0
                            self.axis_states[axis] = fvalue
                            self.ik()
                            # print("{}: {}".format(axis, round(fvalue * 100) / 100))
            except BlockingIOError:
                pass  # this is fine
            except OSError:
                self.joystick = None  # disconnect
                print("joystick disconnected")

        def run(self):
            keep_running = True
            joystick_check_counter = 0
            while keep_running:

                # check and see if a new joystick was connected
                if self.joystick is None and joystick_check_counter == 0:
                    try:
                        os.stat(JOYSTICK_PATH)
                        # this next line doesn't get executed if the joystick isn't found
                        self.joystick = os.open(JOYSTICK_PATH, os.O_RDONLY | os.O_NONBLOCK)
                        print("found joystick")
                        if len(self.axis_map) == 0:
                            self.get_axis_map()
                            self.get_button_map()
                    except OSError:
                        pass  # no joystick found

                if self.joystick is not None:
                    self.handle_joystick()

                joystick_check_counter += 1
                if joystick_check_counter >= CHECK_JOYSTICK_EVERY_N:
                    joystick_check_counter = 0

                if not self.queue.empty():
                    action = self.queue.get()
                    if self.joystick_cmd[0] != 0 and self.joystick_cmd[1] != 0:
                        action = self.joystick_cmd[0]

                    if action == "quit":
                        keep_running = False
                        self.robot.stop()
                    else:
                        if self.halt:
                            self.robot.stop()
                        else:
                            act = self.robot.list_action(action[:2])
                            if len(action) == 5:
                                self.robot.rgb_action(action[2:])

                            self.last_action_time = time.time()
                            self.last_action = act

                else:
                    if self.halt:
                        self.robot.stop()
                    elif self.joystick_cmd[0] != 0 and self.joystick_cmd[1] != 0:
                        self.robot.list_action(self.joystick_cmd)
                        self.last_action_time = time.time()
                        self.last_action = self.joystick_cmd
                    else:

                        # check if it's time to break
                        delta = time.time() - self.last_action_time - DECELERATION_TIMEOUT

                        if 0 <= delta < DECELERATION_BREAK_TIME:
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


class FailsafeController:
    """ Main class for controlling the robot.
    Includes automatic deceleration if no action
    is received for DECELERATION_TIMEOUT

    """

    def __init__(self):
        self.max_speed = float(os.getenv("DUCKIETOWN_MAXSPEED", 0.7))
        print("running with max speed:", self.max_speed)
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

        action = np.clip(action, -1, 1) * self.max_speed
        action = [-action[1], -action[0]]  # because of the wiring, this is weird
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
