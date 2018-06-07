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
        assert len(action) == 2
        msg = construct_action(self.id, action=action)

        # run action on robot
        self.robot_sock.send_string(msg)
        print("sent action:",msg)

        # return last known camera image #FIXME: this must be non-blocking and re-send ping if necessary
        if with_observation:
            return self.cam.get_img_blocking()
        else:
            return None

    def observe(self):
        return self.cam.get_img_blocking()

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

        im = Image.fromarray(np.zeros((160,128,3),dtype=np.uint8))
        self.img = ImageTk.PhotoImage(im)
        self.panel = tkinter.Label(self.rootwindow, image=self.img)

        # The Pack geometry manager packs widgets in rows or columns.
        self.panel.pack(side="bottom", fill="both", expand="yes")

        frame.focus_set()
        self.rootwindow.after(200, self.updateImg)
        self.rootwindow.mainloop()

    def updateImg(self):
        self.rootwindow.after(200, self.updateImg)
        obs = self.robot.observe()
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

    def keysToAction(self):
        action = np.array([0,0])
        if 8320768 in self.history and 8189699 in self.history: # UP/RIGHT
            action = np.array([.3, .9])
        elif 8320768 in self.history and 8124162 in self.history: # UP/LEFT
            action = np.array([.9, .3])
        elif 8255233 in self.history and 8189699 in self.history: # DOWN/RIGHT
            action = np.array([-.3, -.9])
        elif 8255233 in self.history and 8124162 in self.history: # DOWN/LEFT
            action = np.array([-.9, -.3])
        elif 8320768 in self.history: # UP
            action = np.array([.9,.9])
        elif 8189699 in self.history: # RIGHT
            action = np.array([-.7,.7])
        elif 8255233 in self.history: # DOWN
            action = np.array([-.8,-.8])
        elif 8124162 in self.history: # LEFT
            action = np.array([.7,-.7])
        return action

