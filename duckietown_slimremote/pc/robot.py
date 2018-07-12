import tkinter
import numpy as np
from PIL import ImageTk, Image

from duckietown_slimremote.helpers import random_id
from duckietown_slimremote.networking import make_push_socket, construct_action
from duckietown_slimremote.pc.camera import SubCameraMaster


class RemoteRobot():
    def __init__(self, host):
        self.host = host

        self.id = random_id()
        self.ping_msg = construct_action(self.id)
        self.robot_sock = make_push_socket(host)
        self.robot_sock.send_string(self.ping_msg)

        self.cam = SubCameraMaster(host)

    def step(self, action, with_observation=True):
        assert len(action) == 2 or len(action) == 5
        msg = construct_action(self.id, action=action)

        # run action on robot
        self.robot_sock.send_string(msg)
        print("sent action:",msg)

        # return last known camera image #FIXME: this must be non-blocking and re-send ping if necessary
        if with_observation:
            return self.cam.get_img_nonblocking()
        else:
            return None

    def observe(self):
        return self.cam.get_img_nonblocking()

    def reset(self):
        # This purposefully doesn't do anything on the real robot (other than halt).
        # But in sim this obviously resets the simulation
        return self.step([0, 0])


class KeyboardControlledRobot():
    def __init__(self, host):
        self.robot = RemoteRobot(host)

        self.rootwindow = tkinter.Tk()

        self.history = []

        frame = tkinter.Frame(self.rootwindow, width=1, height=1)
        frame.bind("<KeyPress>", self.keydown)
        frame.bind("<KeyRelease>", self.keyup)
        frame.pack()

        # Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.

        im = Image.fromarray(np.zeros((160,120,3),dtype=np.uint8))
        self.img = ImageTk.PhotoImage(im)
        self.panel = tkinter.Label(self.rootwindow, image=self.img)

        # The Pack geometry manager packs widgets in rows or columns.
        self.panel.pack(side="bottom", fill="both", expand="yes")

        self.robot.step([0,0], with_observation=False) # init socket if it isn't

        frame.focus_set()
        self.rootwindow.after(200, self.updateImg)
        self.rootwindow.mainloop()

    def updateImg(self):
        self.rootwindow.after(200, self.updateImg)
        obs = self.robot.observe()
        if obs is not None:
            img2 = ImageTk.PhotoImage(Image.fromarray(obs))
            self.panel.configure(image=img2)
            self.panel.image = img2

        return

    def keyup(self, e):
        if e.keycode in self.history:
            self.history.pop(self.history.index(e.keycode))
        self.moveRobot()

    def moveRobot(self):
        action = self.keysToAction()
        _ = self.robot.step(action, with_observation=False)

    def keydown(self, e):
        if not e.keycode in self.history:
            self.history.append(e.keycode)
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
        if 8255233 in self.history or 113 in self.history:
            return True
        return False

    def _key_right(self):
        if 8124162 in self.history or 114 in self.history:
            return True
        return False

    def keysToAction(self):
        # mac / lin keycodes
        action = np.array([0,0])
        if self._key_up() and self._key_right(): # UP/RIGHT
            action = np.array([1, .4])
        elif self._key_up() and self._key_left(): # UP/LEFT
            action = np.array([.4, 1])
        elif self._key_down() and self._key_right(): # DOWN/RIGHT
            action = np.array([-1, -.4])
        elif self._key_down() and self._key_left(): # DOWN/LEFT
            action = np.array([-.4, -1])
        elif self._key_up(): # UP
            action = np.array([.7,.7])
        elif self._key_right(): # RIGHT
            action = np.array([.4,.0])
        elif self._key_down(): # DOWN
            action = np.array([-.4,-.4])
        elif self._key_left(): # LEFT
            action = np.array([0,.4])
        return action

