import time

from picamera import PiCamera
from picamera.array import PiRGBArray

camera = PiCamera()

for format in ["bgr", "rgb"]:
    for resolution in [(160, 128), (320, 240)]:
        for framerate in range(30, 100, 10):
            # resolution = (320, 240)
            # framerate = 80

            # print ("max framerate: ",camera.MAX_FRAMERATE)
            camera.resolution = resolution
            # camera.rotation = rotation
            camera.framerate = framerate
            # camera.hflip = hflip
            # camera.vflip = vflip
            rawCapture = PiRGBArray(camera, size=resolution)
            stream = camera.capture_continuous(rawCapture,
                                               format=format,
                                               use_video_port=True)
            frame = None

            timings = 0
            tests = 1000

            start = time.time()
            for idx, f in enumerate(stream):
                frame = f.array
                rawCapture.truncate(0)
                timings += time.time() - start
                if idx == tests:
                    break
                start = time.time()

            frametime = timings / tests
            hz = 1 / frametime
            print("res:{}, framerate:{}, format:{}, avg {}s per frame, i.e. {}Hz".format(
                resolution, framerate, format,
                round(frametime, 4), round(hz, 4)))

        frame = None
        stream = None
        rawCapture = None

# res:(160, 128), framerate:30, format:bgr, avg 0.0334s per frame, i.e. 29.9217Hz
# res:(160, 128), framerate:40, format:bgr, avg 0.0251s per frame, i.e. 39.9025Hz
# res:(160, 128), framerate:50, format:bgr, avg 0.02s per frame, i.e. 49.9275Hz
# res:(160, 128), framerate:60, format:bgr, avg 0.0167s per frame, i.e. 59.9627Hz
# res:(160, 128), framerate:70, format:bgr, avg 0.0143s per frame, i.e. 69.9602Hz
# res:(160, 128), framerate:80, format:bgr, avg 0.016s per frame, i.e. 62.6957Hz
# res:(160, 128), framerate:90, format:bgr, avg 0.0345s per frame, i.e. 29.0043Hz
# res:(320, 240), framerate:30, format:bgr, avg 0.0334s per frame, i.e. 29.9212Hz
# res:(320, 240), framerate:40, format:bgr, avg 0.0251s per frame, i.e. 39.9Hz
# res:(320, 240), framerate:50, format:bgr, avg 0.02s per frame, i.e. 49.9238Hz
# res:(320, 240), framerate:60, format:bgr, avg 0.0167s per frame, i.e. 59.9616Hz
# res:(320, 240), framerate:70, format:bgr, avg 0.0178s per frame, i.e. 56.0315Hz
# res:(320, 240), framerate:80, format:bgr, avg 0.0279s per frame, i.e. 35.8044Hz
# res:(320, 240), framerate:90, format:bgr, avg 0.0256s per frame, i.e. 39.0926Hz
# res:(160, 128), framerate:30, format:rgb, avg 0.0334s per frame, i.e. 29.9229Hz
# res:(160, 128), framerate:40, format:rgb, avg 0.0251s per frame, i.e. 39.9028Hz
# res:(160, 128), framerate:50, format:rgb, avg 0.02s per frame, i.e. 49.9274Hz
# res:(160, 128), framerate:60, format:rgb, avg 0.0167s per frame, i.e. 59.9612Hz
# res:(160, 128), framerate:70, format:rgb, avg 0.0143s per frame, i.e. 69.8926Hz
# res:(160, 128), framerate:80, format:rgb, avg 0.0195s per frame, i.e. 51.2392Hz
# res:(160, 128), framerate:90, format:rgb, avg 0.0327s per frame, i.e. 30.5962Hz
# res:(320, 240), framerate:30, format:rgb, avg 0.0334s per frame, i.e. 29.9211Hz
# res:(320, 240), framerate:40, format:rgb, avg 0.0251s per frame, i.e. 39.8999Hz
# res:(320, 240), framerate:50, format:rgb, avg 0.02s per frame, i.e. 49.9234Hz
# res:(320, 240), framerate:60, format:rgb, avg 0.0167s per frame, i.e. 59.9606Hz
# res:(320, 240), framerate:70, format:rgb, avg 0.018s per frame, i.e. 55.6693Hz
# res:(320, 240), framerate:80, format:rgb, avg 0.029s per frame, i.e. 34.5309Hz
# res:(320, 240), framerate:90, format:rgb, avg 0.0256s per frame, i.e. 39.0926Hz
