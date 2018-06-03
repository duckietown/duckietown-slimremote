from queue import Queue
from threading import Thread

import cv2
import numpy as np

from duckietown_slimremote.networking import make_pub_socket, send_array
from duckietown_slimremote.robot.constants import CAM_FAILURE_COUNTER


class Camera():
    def __init__(self, res=(320, 240), fps=90):
        self.cap = cv2.VideoCapture(0)

        # properties are listed here:
        # https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-get
        self.cap.set(3, res[0])
        self.cap.set(4, res[1])
        self.cap.set(21, 3)

        # framerate is capped to 90Hz on old PiCam firmware
        # can be updated to 120Hz
        fps = min(60, fps)
        self.cap.set(5, fps)
        print("camera running with {}x{} px at {}Hz".format(res[0], res[1], fps))

    def observe(self):
        ret = False

        i = 0

        while not ret:
            ret, frame = self.cap.read()
            i += 1
            if i == CAM_FAILURE_COUNTER:
                raise Exception("Camera produced too many faulty images - "
                                "might be overheating."
                                "Please inspect robot.")

        # frame is recorded in OpenCV BGR, but here we
        # invert color channel order to get RGB.
        # Also make sure that the array is C-contiguous
        # which we need it to be for the transmission
        return np.asarray(frame[:, :, ::-1], order='C')


class ThreadedPubCamera(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.publisher_sockets = []
        self.cam = Camera(res=(160, 128))

    def run(self):
        # look for new subscribers from queue
        # get camera image
        # send image to all subscribers

        keep_running = True
        while keep_running:
            if not self.queue.empty():
                cmd = self.queue.get()
                if cmd == "kill":
                    keep_running = False
                    break  # redundant I guess
                else:
                    # we assume that then the cmd is an IP address
                    self.publisher_sockets.append(make_pub_socket(cmd, for_images=True))

            img = self.cam.observe()

            for pub in self.publisher_sockets:
                send_array(pub, img)


class CameraController():

    def __init__(self) -> None:
        self.cam_queue = Queue()
        self.cam = ThreadedPubCamera(self.cam_queue)
        self.cam.daemon = True  # so that you can kill the thread
        self.cam.start()
        self.cam_subscribers = []

    def addSubscriber(self, ip):
        if ip not in self.cam_subscribers:
            self.cam_queue.put(ip)
            self.cam_subscribers.append(ip)
