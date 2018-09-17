# duckietown-slimremote

[![Docker Hub](https://img.shields.io/docker/pulls/duckietown/duckietown-slimremote.svg)](https://hub.docker.com/r/duckietown/duckietown-slimremote)

The duckietown-slimremote is a slim control interface for teleoperating a Duckiebot. It relays control inputs from a laptop to the Duckiebot and publishes images from the Duckiebot's onboard camera to a graphical user interface.

This library is integrated in the following applications:

* [duckietown/gym-duckietown](https://github.com/duckietown/gym-duckietown)
* [duckietown/gym-duckietown-agent](https://github.com/duckietown/gym-duckietown-agent)
* [duckietown/duckie-ros](https://github.com/duckietown/duckie-ros)

## Docker

If your Duckiebot is running HypriotOS/DuckieOS, you can run `duckietown/duckietown-slimremote` in a Docker container.

The following command will start the motor contoller and image server on the Duckiebot:

    docker run -dit -p 5558:5558 --privileged duckietown/duckietown-slimremote

Once the motor controller and image server are started, you can control the Duckiebot via the keyboard on a PC or Mac:

```
docker run -it \
	--entrypoint=qemu-arm-static \
	--volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
	duckietown/duckietown-slimremote /bin/sh -c "python tests/12-test-keyboard-controller.py"
```

### Building 

To build the image locally (i.e. on an x86 laptop), run the following command from root directory of this project:

    docker build --tag duckietown/duckietown-slimremote .

## Manual Installation

**On the robot:**

First you need to compile the [most recent version of OpenCV](https://raspberrypi.stackexchange.com/questions/69169/how-to-install-opencv-on-raspberry-pi-3-in-raspbian-jessie).

After that, clone and install this repo:

    git clone https://github.com/duckietown/duckietown-slimremote.git && \
    cd duckietown-slimremote && \
    sudo pip3 install -e . # Install to root user in developer mode
    
Once the repo is installed you can start the robot controller:

    duckietown-start-robot2
    
To quit the robot controller, press <kbd>Ctrl</kbd>+<kbd>c</kbd>.
    
**On the PC:**

To run duckietown-slimremote on a PC or Mac, use the same installation procedure as the robot, however the OpenCV version is not important and the standard package manager should suffice (e.g. on Mac OS you can use `brew install opencv3 --with-contrib --with-python3 --without-python` for Python 3 bindings).

## Running

To launch duckietown-slimremote, run the following command from the project root directory:

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
