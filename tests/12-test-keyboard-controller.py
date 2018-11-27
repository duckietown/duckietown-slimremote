import sys
from duckietown_slimremote.pc.robot import KeyboardControlledRobot

host = "duckmylife3.local"
print ("connecting to host",host)
if len(sys.argv) > 1:
    host = sys.argv[1]

kbd = KeyboardControlledRobot(host, 15)
