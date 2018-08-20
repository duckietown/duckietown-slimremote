## Docker version (if your Duckiebot is running HypriotOS/DuckieOS):

To build the image locally (i.e. on an x86 laptop), run this command:

    docker build --file docker/robot/Dockerfile --tag duckietown-slimremote .

Run this on the Duckiebot to start the motor command and image server:

    docker run -dit --privileged duckietown/duckietown-slimremote-robot

TODO: more documentation on the remote side of this, i.e. how does somebody connect to this docker?

## Install

**On the robot:**

First you need to compile the most recent version of OpenCV: https://raspberrypi.stackexchange.com/questions/69169/how-to-install-opencv-on-raspberry-pi-3-in-raspbian-jessie

After that clone and install the repo:

    git clone https://github.com/duckietown/duckietown-slimremote.git
    
    cd duckietown-slimremote
    
    sudo pip3 install -e . # install in developer mode
    
Once the repo is installed you can start the robot controller:

    duckietown-start-robot2
    
You quit the robot controller via <kbd>CTRL</kbd>+<kbd>c</kbd>.
    
**On the PC:**

To run duckietown-slimremote on a PC or Mac, use the same installation procedure as the robot, but the OpenCV version is not important and the standard package manager should suffice (e.g. on Mac OS you can use `brew install opencv3 --with-contrib --with-python3 --without-python` for Python 3 bindings).

Afterwards you can run:

    python3 tests/12-test-keyboard-controller.py
    
This will open a GUI controller that displays the robot's camera, and in which you drive the Duckiebot via the arrow keys (<kbd>↑</kbd>,<kbd>↓</kbd>,<kbd>←</kbd>,<kbd>→</kbd>), which are mapped to motor oututs.

## API

The main remote control class is [duckietown_slimremote.pc.robot.RemoteRobot](duckietown_slimremote/pc/robot.py), whose primary interface is the following three methods:

### RemoteRobot.step(action, with_observation=True)

Executes a single motor command. Action is either a tuple, list, or numpy array of two elements. Returns an observation that is an RGB image (unless `with_observation = False`) in the shape `(160,128,3)`. This is a blocking call and is rate limited by the image observation frequency, currently capped at 60Hz.
 
### RemoteRobot.observe()

Returns the last seen observation without taking an action. Like `step(action, with_observation=True)`, this returns an RGB image and is blocking call, capped at 60Hz.
 
### RemoteRobot.reset():

Stops the robot (sends a `[0,0]` action).

## Communication & Architecture

![image depicting the different components and how they interact](doc/overview.png "Architecture Overview")
