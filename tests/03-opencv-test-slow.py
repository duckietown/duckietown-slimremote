import random
import time

import numpy as np
import cv2

cap = cv2.VideoCapture(0)

for i in range(19):
    print(i, cap.get(i))

# properties are listed here:
# https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-get

cap.set(3, 320)
cap.set(4, 240)
cap.set(5, 90)  # framerate (90Hz is PiCam limit on old firmware)

tests = 10
timings = 0

i = 0
while (True):
    # Capture frame-by-frame
    start = time.time()
    ret, frame = cap.read()

    if not ret:
        print("something wrong")
    else:
        print("got frame")

    i += 1

    if i == tests:
        break

    time.sleep(random.random()*3)



cap.release()

