import sys
from duckietown_slimremote.pc.robot import KeyboardControlledRobot

host = "localhost"
if len(sys.argv) > 1:
    host = sys.argv[1]

kbd = KeyboardControlledRobot(host)
