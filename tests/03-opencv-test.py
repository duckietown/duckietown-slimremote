import time

import cv2

cap = cv2.VideoCapture(0)

for i in range(19):
    print(i, cap.get(i))

# properties are listed here:
# https://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-get

for res in [(160, 128), (320, 240)]:
    for fps in range(30, 100, 10):
        cap.set(3, res[0])
        cap.set(4, res[1])
        cap.set(5, fps)  # framerate (90Hz is PiCam limit on old firmware)

        tests = 1000
        timings = 0

        i = 0
        while True:
            # Capture frame-by-frame
            start = time.time()
            ret, frame = cap.read()

            # print(frame.shape, frame.dtype)
            # import matplotlib.pyplot as plt
            #
            # plt.imshow(frame[:,:,::-1], interpolation="nearest")
            # plt.show()
            # quit()

            i += 1
            timings += time.time() - start
            if i == tests:
                break

        # When everything done, release the capture

        fr = timings / tests

        print("res:{}, fps:{}, avg frame time {}s aka {}Hz".format(
            res,
            fps,
            round(fr, 4),
            round(1 / fr, 4)
        ))

cap.release()

## results:
# res:(160, 128), fps:30, avg frame time 0.0337s aka 29.6666Hz
# res:(160, 128), fps:40, avg frame time 0.0255s aka 39.2372Hz
# res:(160, 128), fps:50, avg frame time 0.0205s aka 48.8868Hz
# res:(160, 128), fps:60, avg frame time 0.0171s aka 58.3842Hz
# res:(160, 128), fps:70, avg frame time 0.0147s aka 67.818Hz
# res:(160, 128), fps:80, avg frame time 0.013s aka 77.0948Hz
# res:(160, 128), fps:90, avg frame time 0.0116s aka 86.5032Hz
# res:(320, 240), fps:30, avg frame time 0.0338s aka 29.5616Hz
# res:(320, 240), fps:40, avg frame time 0.0255s aka 39.1948Hz
# res:(320, 240), fps:50, avg frame time 0.0205s aka 48.8292Hz
# res:(320, 240), fps:60, avg frame time 0.0171s aka 58.3892Hz
# res:(320, 240), fps:70, avg frame time 0.0147s aka 67.8207Hz
# res:(320, 240), fps:80, avg frame time 0.013s aka 77.1904Hz
# res:(320, 240), fps:90, avg frame time 0.0116s aka 86.4589Hz
