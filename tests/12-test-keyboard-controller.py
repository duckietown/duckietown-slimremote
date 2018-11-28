import sys
from duckietown_slimremote.pc.robot import KeyboardControlledRobot

# host = "duckmylife3.local"

if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    print("usage: python3 12-test-keyboard-controller.py ![hostname]")
    exit(0)

print("connecting to host", host)
kbd = KeyboardControlledRobot(host)
