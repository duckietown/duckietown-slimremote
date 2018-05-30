import time

import picamera
import picamera.array

TESTS = 10
timings = 0
size = (320, 240)

with picamera.PiCamera() as camera:
    camera.resolution = size
    with picamera.array.PiRGBArray(camera, size=size) as output:
        for _ in range(TESTS):
            start = time.time()
            camera.capture(output, 'bgr', resize=size)
            output.truncate(0)
            diff = time.time() - start
            timings += diff
            # print (output.array.shape)
        print ("ran {} tests with an avera of {}s".format(TESTS,timings/TESTS))