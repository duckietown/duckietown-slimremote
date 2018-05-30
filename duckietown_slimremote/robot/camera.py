import cv2
import numpy as np
from duckietown_slimremote.robot.constants import CAM_FAILURE_COUNTER


class Camera():
    def __init__(self, res=(320, 240), fps=90):
        self.cap = cv2.VideoCapture(0)

        # properties are listed here:
        # https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-get
        self.cap.set(3, res[0])
        self.cap.set(4, res[1])

        # framerate is capped to 90Hz on old PiCam firmware
        # can be updated to 120Hz
        fps = min(90, fps)
        self.cap.set(5, fps)

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
        # Also make sure that teh array is C-contiguous.
        return np.asarray(frame[:, :, ::-1], order='C')

