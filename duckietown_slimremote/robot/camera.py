import json
from multiprocessing import Process
from threading import Thread

import cv2
import numpy as np
import zmq

from picamera import PiCamera
from picamera.array import PiRGBArray

from duckietown_slimremote.helpers import get_right_queue, string_convert
from duckietown_slimremote.networking import make_pub_socket, send_gym, get_port
from duckietown_slimremote.robot.constants import CAM_FAILURE_COUNTER


class Camera:
    def __init__(self, res=(160, 120), fps=30):
        self.cap = cv2.VideoCapture(-1)

        # for i in range(50):
        #     print(i, self.cap.get(i))

        # properties are listed here:
        # https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-get
        self.cap.set(3, res[0])
        self.cap.set(4, res[1])
        try:
            self.cap.set(21, 3)
        except:
            print("WARNING: loaded cam driver doesn't support setting buffer size")

        # framerate is capped to 90Hz on old PiCam firmware
        # can be updated to 120Hz
        fps = min(30, fps)
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

            while True:
                if not self.queue.empty():
                    cmd = self.queue.get()
                    if cmd == "kill":
                        break
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


def make_async_camera2(base):
    """ allows to instantiate the camera as thread or as process

    :param base: options are Thread|Process
    :return:
    """

    class AsyncPubCamera2(base):
        def __init__(self, queue, res=(160, 128), fps=50):
            super(AsyncPubCamera2, self).__init__()
            # Thread.__init__(self)
            self.queue = queue
            # self.publisher_socket = None
            # self.context = zmq.Context()
            self.cam = PiCamera()

            self.cam.resolution = res
            self.cam.framerate = fps

            fps = min(50, fps)
            self.cam.framerate = fps
            self.res = res

            print("picamera running with {}x{} px at {}Hz".format(res[0], res[1], fps))

        def run(self):
            raw = PiRGBArray(self.cam, size=self.res)
            stream = self.cam.capture_continuous(raw,
                                                 format="rgb",
                                                 use_video_port=True)
            # wait for first subscriber
            # then create socket
            # get camera image
            # broadcast image

            publisher_socket = None
            md = None

            # if misc is None:
            misc = {"challenge": None}
            misc = string_convert(json.dumps(misc))

            topic = string_convert(u"0")

            rew = string_convert(str(0))
            done = string_convert(str(False))

            for idx, f in enumerate(stream):
                frame = f.array
                if md is None:
                    md = {
                        "dtype": str(frame.dtype),
                        "shape": frame.shape,
                    }
                    md = string_convert(json.dumps(md))
                if not self.queue.empty():
                    cmd = self.queue.get()
                    if cmd == "kill":
                        break
                    else:
                        if publisher_socket is None:
                            port = get_port(True)

                            print("starting pub socket on port %s" % port)
                            context_ = zmq.Context()
                            publisher_socket = context_.socket(zmq.PUB)
                            publisher_socket.bind("tcp://*:{}".format(port))

                # the pub / send_array method only works once the first subscriber is connected
                if publisher_socket is not None:
                    # on the real robot we are sending 0 reward, in simulation the reward is a float
                    # we also send done=False because the real robot doesn't know when to stop ^^
                    # send_gym(publisher_socket, frame, 0, False)
                    publisher_socket.send_multipart([topic, md, frame, rew, done, misc])
                raw.truncate(0)

    queue = get_right_queue(base)

    return AsyncPubCamera2, queue


class CameraController:
    def __init__(self):
        # cam_class = make_async_camera(Thread)
        cam_class, cam_queue = make_async_camera2(Thread)  # picamera needs Thread, cv2 can use Process
        self.cam_queue = cam_queue()

        self.cam = cam_class(self.cam_queue)
        self.cam.daemon = True  # so that you can kill the thread
        self.cam.start()

    def init(self):
        self.cam_queue.put("init")
