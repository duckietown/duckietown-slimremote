from queue import Queue

from duckietown_slimremote.networking import make_pull_socket, has_pull_message, receive_data
from duckietown_slimremote.robot.camera import CameraController
from duckietown_slimremote.robot.motors import FailsafeController

# start camera thread
# start motor thread
# start subscriber sub

cam = CameraController()
motors = FailsafeController()

sock, poll = make_pull_socket()

# main loop, look for new incoming connections

print("Robot listening to incoming connections...")

cam_started = False

while True:
    if has_pull_message(sock, poll):
        success, data = receive_data(sock)
        if not success:
            print(data)  # in error case, this will contain the err msg
            continue

        if data["topic"] == 0:
            motors.run(data["msg"])

        if not cam_started:
            cam.init()
            cam_started = True

        if data["topic"] == 1:
            print("received ping:", data)

        if data["topic"] == 2:
            print("received reset. "
                  "On the real robot this doesn't do anything. "
                  "In simulation this resets the simulator")
