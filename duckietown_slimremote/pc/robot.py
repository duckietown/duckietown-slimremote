import time
from math import ceil
from importlib import import_module
import numpy as np

from duckietown_slimremote import logger
from duckietown_slimremote.helpers import random_id
from duckietown_slimremote.networking import make_push_socket, construct_action, RESET, host_is_reachable
from duckietown_slimremote.pc.camera import SubCameraMaster


# cd /workspace/src/duckietown-slimremote/ && git config --global user.email "you@example.com" && \
# git config --global user.name "Your Name" && git pull origin testing; git reset --hard origin/testing


class RemoteRobot:
    def __init__(self, host, shape=(640, 480, 3), dtype=np.uint8, silent=False):
        logger.info('Slimremote trying to connect to "{}"'.format(host))
        reachable = host_is_reachable(host)
        logger.info("'ping' reports host is " + ("REACHABLE" if reachable else "NOT reachable"))

        self.host = host
        self.silent = silent

        # Create a somewhat random ID for this connection.
        # The randomness isn't super important since there
        # will only ever be 1-2 clients connected to the same
        # server
        self.id = random_id()

        # Construct a "hello world" messag
        self.ping_msg = construct_action(self.id)

        # Initialize the PUSH socket
        self.robot_sock = make_push_socket(host)

        self.cam = SubCameraMaster(host, silent=self.silent, shape=shape, dtype=dtype)

        # We have to wait for the thread to launch
        self.cam.wait_until_ready()

        # say hi to the robot
        self._ping()

    def _ping(self):
        # Send the initialization string.
        self.robot_sock.send_string(self.ping_msg)

    def step(self, action, with_observation=True):
        assert len(action) == 2 or len(action) == 5
        msg = construct_action(self.id, action=action)

        # before we send an action, we zero the last
        # observation to prevent caching errors
        self.cam.empty_cache()

        # run action on robot
        self.robot_sock.send_string(msg)
        # print("sent action:", msg)

        # return last known camera image #FIXME: this must be non-blocking and re-send ping if necessary
        if with_observation:
            return self._failsafe_observe(msg)
        else:
            return None

    def _failsafe_observe(self, msg):
        """ This function is there to deal with the simulator not being ready
        which sometimes happens right after the start. This function gives
        the simulator server two times 3s to come up with a response.

        :param msg: the action message that was sent to the server
                    in case we need to send it again
        """

        obs, rew, done, misc = self.cam.get_new_observation()

        def not_ready():
            return np.count_nonzero(obs) == 0

        ncounts = 5
        wait = 1
        while not_ready():
            # then the simulator probably wasn't ready
            # and we send the action again
            logger.info('Simulator not ready - wait 1 second and try again')
            self.robot_sock.send_string(msg)
            time.sleep(wait)
            obs, rew, done, misc = self.cam.get_new_observation()
            ncounts -= 1
            if ncounts == 0:
                # if this happens twice then we can assume the server is offline
                msg = "Giving up to connect to the gym duckietown server at host: %s" % self.host
                raise Exception(msg)

        return obs, rew, done, misc

    def observe(self):
        """ returns the last observation

        :return:
        """
        return self.cam.get_cached_observation()

    def reset(self):
        msg = construct_action(self.id, action=RESET)
        self.robot_sock.send_string(msg)
        obs, _, _, _ = self.observe()
        return obs
        # print("sent reset")


class KeyboardControlledRobot:
    def __init__(self, host, fps=15, shape=(640, 480, 3), dtype=np.uint8):

        # this is a bit nasty, but we only need to import this when the keyboard controller is needed
        self.tkinter = import_module("tkinter")
        self.ImageTk = import_module("PIL.ImageTk")
        self.Image = import_module("PIL.Image")

        self.robot = RemoteRobot(host, shape, dtype)

        self.rootwindow = self.tkinter.Tk()

        self.history = []

        self.last_obs = None

        frame = self.tkinter.Frame(self.rootwindow, width=1, height=1)
        frame.bind("<KeyPress>", self.keydown)
        frame.bind("<KeyRelease>", self.keyup)
        frame.pack()

        # Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.

        im = self.Image.fromarray(np.zeros(shape, dtype=dtype))
        self.img = self.ImageTk.PhotoImage(im)
        self.panel = self.tkinter.Label(self.rootwindow, image=self.img)

        # The Pack geometry manager packs widgets in rows or columns.
        self.panel.pack(side="bottom", fill="both", expand="yes")

        self.robot.step([0, 0], with_observation=False)  # init socket if it isn't

        frame.focus_set()
        self.fps = fps
        self.last_cmd_time = time.time()
        self.rootwindow.after(int(ceil(1000 / fps)), self.updateImg)
        self.rootwindow.mainloop()

    def updateImg(self):
        self.rootwindow.after(int(ceil(1000 / self.fps)), self.updateImg)
        obs, rew, done, misc = self.robot.observe()
        if obs is not None and np.count_nonzero(obs) > 0:
            img2 = self.ImageTk.PhotoImage(self.Image.fromarray(obs))
            self.panel.configure(image=img2)
            self.panel.image = img2
            # if not (self.last_obs == obs).all():
            same_img = (self.last_obs == obs)
            if (type(same_img) == type(True) and not same_img) or not same_img.all():
                print("reward: {}, done: {}".format(rew, done))
                self.last_obs = obs

        return

    def keyup(self, e):
        print("key up:", e.keycode)
        if e.keycode in self.history:
            self.history.pop(self.history.index(e.keycode))

        self.moveRobot()

    def moveRobot(self):
        action = self.keysToAction()
        if len(action) > 0 and action[0] != RESET:
            _ = self.robot.step(action, with_observation=False)
        else:
            self.robot.reset()

    def keydown(self, e):
        print("key down:", e.keycode)
        if not e.keycode in self.history:
            self.history.append(e.keycode)

        # limit the transmission while key held down
        if time.time() - self.last_cmd_time > (1 / self.fps):
            self.last_cmd_time = time.time()
            self.moveRobot()

    def _key_up(self):
        if 8320768 in self.history or 111 in self.history:
            return True
        return False

    def _key_down(self):
        if 8255233 in self.history or 116 in self.history:
            return True
        return False

    def _key_left(self):
        if 8124162 in self.history or 113 in self.history:
            return True
        return False

    def _key_right(self):
        if 8189699 in self.history or 124 in self.history:
            return True
        return False

    def _key_reset(self):  # "r" key, don't know the mac key right now
        if 27 in self.history:
            return True
        return False

    def keysToAction(self):
        # mac / lin keycodes

        # it is utterly possible that I plugged in the wires opposite way around. :/
        action = np.array([0, 0])
        if self._key_up() and self._key_right():  # UP/RIGHT
            action = np.array([-.4, -.7])
        elif self._key_up() and self._key_left():  # UP/LEFT
            action = np.array([-.7, -.4])
        elif self._key_down() and self._key_right():  # DOWN/RIGHT
            action = np.array([.4, .7])
        elif self._key_down() and self._key_left():  # DOWN/LEFT
            action = np.array([.7, .4])
        elif self._key_up():  # UP
            action = np.array([-.7, -.7])
        elif self._key_right():  # RIGHT
            action = np.array([.4, -.4])
        elif self._key_down():  # DOWN
            action = np.array([.7, .7])
        elif self._key_left():  # LEFT
            action = np.array([-.4, .4])

        if self._key_reset():
            action = [RESET]
        return action
