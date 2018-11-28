import sys
from duckietown_slimremote.pc.robot import KeyboardControlledRobot

<<<<<<< HEAD
host = "duckmylife3.local"
print ("connecting to host",host)
if len(sys.argv) > 1:
    host = sys.argv[1]

kbd = KeyboardControlledRobot(host, 15)
=======


if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    print ("usage: python3 12-test-keyboard-controller.py ![hostname]")
    exit(0)
    
print ("connecting to host",host)
kbd = KeyboardControlledRobot(host)
>>>>>>> d01e685788e07f5b26955a8c5b24f53aaa2daed6
