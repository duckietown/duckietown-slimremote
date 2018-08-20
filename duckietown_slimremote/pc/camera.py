import time
from threading import Event, Thread

import numpy as np
import zmq
import matplotlib

# matplotlib.use('TkAgg')  # needed for tkinter GUI
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from duckietown_slimremote.helpers import timer, Frame
from duckietown_slimremote.networking import make_sub_socket, recv_gym


class ThreadedSubCamera(Thread):
    def __init__(self, frame, event_img, event_ready, host, silent=False):
        super(ThreadedSubCamera, self).__init__()
        self.silent = silent
        self.frame = frame
        self.event_img = event_img
        self.event_ready = event_ready

        context = zmq.Context()
        self.sock = make_sub_socket(for_images=True, context_=context, target=host)

    def run(self):
        # block while waiting for image
        # put image into shared memory

        keep_running = True
        timings = []
        start = time.time()
        while keep_running:
            self.event_ready.set()  # we basically only need this once

            img, rew, done, misc = recv_gym(self.sock)

            np.copyto(self.frame.obs, img)
            self.frame.rew = rew
            self.frame.done = done
            self.frame.misc.update(misc)
            self.event_img.set()

            if not self.silent:
                timings, start = timer(timings, start)


class SubCameraMaster():
    # controls and communicates with the threaded sub camera
    def __init__(self, host, silent=False):
        self.frame = Frame()
        self.event_img = Event()
        self.event_ready = Event()

        self.cam_thread = ThreadedSubCamera(self.frame, self.event_img, self.event_ready, host, silent=silent)
        self.cam_thread.daemon = True
        self.cam_thread.start()

    def get_cached_observation(self):
        return self.frame.to_gym()

    def get_new_observation(self):
        self.event_img.wait(timeout=3)  # 3 second timeout, if no response we send action again
        self.event_img.clear()

        return self.get_cached_observation()

    def wait_until_ready(self):
        self.event_ready.wait()

    def empty_cache(self):
        np.copyto(dst=self.frame.obs, src=np.zeros((120, 160, 3), dtype=np.uint8))


def cam_window_init():
    ### THIS IS SHITTY AND SLOW, USE OPENCV INSTEAD
    plt.ion()
    img = np.random.uniform(0, 255, (256, 512, 3))
    img_container = plt.imshow(img, interpolation='none', animated=True, label="blah")
    img_window = plt.gca()
    return (img_container, img_window)


def cam_window_update(img, img_container, img_window):
    # THIS IS SHITTY AND SLOW, USE OPENCV INSTEAD
    img_container.set_data(img)
    img_window.plot([0])
    plt.pause(0.001)

# def cam_windows_init_opencv(res=(160, 120, 3)):
#     import cv2
#     cv2.imshow('livecam', np.zeros(res))
#     cv2.waitKey(1)
#
#
# def cam_windows_update_opencv(img):
#     cv2.imshow('livecam', img[:, :, ::-1])
#     cv2.waitKey(1)
