from multiprocessing import Process
from threading import Thread

import cv2
import numpy as np
import zmq

from duckietown_slimremote.helpers import get_right_queue
from duckietown_slimremote.networking import make_pub_socket, send_gym
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


def make_async_camera(base):
    """ allows to instantiate the camera as thread or as process

    :param base: options are Thread|Process
    :return:
    """

    class AsyncPubCamera(base):
        def __init__(self, queue):
            super(AsyncPubCamera, self).__init__()
            # Thread.__init__(self)
            self.queue = queue
            self.publisher_socket = None
            self.cam = Camera(res=(160, 120))
            self.context = zmq.Context()

        def run(self):
            # wait for first subscriber
            # then create socket
            # get camera image
            # broadcast image

            keep_running = True
            while keep_running:
                if not self.queue.empty():
                    cmd = self.queue.get()
                    if cmd == "kill":
                        keep_running = False
                        break  # redundant I guess
                    else:
                        if self.publisher_socket is None:
                            self.publisher_socket = make_pub_socket(
                                for_images=True,
                                context_=self.context
                            )

                # the pub / send_array method only works once the first subscriber is connected
                if self.publisher_socket is not None:
                    img = self.cam.observe()
                    # on the real robot we are sending 0 reward, in simulation the reward is a float
                    # we also send done=False because the real robot doesn't know when to stop ^^
                    send_gym(self.publisher_socket, img, 0, False)

    queue = get_right_queue(base)

    return AsyncPubCamera, queue


class CameraController():

    def __init__(self) -> None:
        # cam_class = make_async_camera(Thread)
        cam_class, cam_queue = make_async_camera(Process)
        self.cam_queue = cam_queue()

        self.cam = cam_class(self.cam_queue)
        self.cam.daemon = True  # so that you can kill the thread
        self.cam.start()

    def init(self):
        self.cam_queue.put("init")
