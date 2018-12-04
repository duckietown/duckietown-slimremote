import sys
import time

from duckietown_slimremote.pc.robot import KeyboardControlledRobot, RemoteRobot

host = "duckmylife3.local"

FPS = 15

if len(sys.argv) > 1:
    host = sys.argv[1]
# else:
#     print("usage: python3 16-test-motor-commands-no-tk.py ![hostname]")
#     exit(0)

print("connecting to host", host)
robot = RemoteRobot(host)

# init
robot.reset()  # this is a dummy function on the real robot
robot.step([0, 0], with_observation=False)  # init socket if it isn't

