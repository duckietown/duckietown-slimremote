# How does the ZMQ communication work?

In addition to this documentation please also look at the networking code in 
[`duckietown_slimremote/networking.py`](https://github.com/duckietown/duckietown-slimremote/blob/master/duckietown_slimremote/networking.py).

## Robot/Sim side

The robot/sim side opens a PULL socket on start (`zmq.PULL`), on port `5558`, that is listening to single line strings from all IP addresses.

There are three possible messages types for the PUSH/PULL socket:

1. Ping/"heartbeat" messages (`topic = 0`), to introduce the  image subscriber and start the camera (if not already done). This is mandatory at the very beginning of every program that controls or observes the robot in order to make sure the PC will receive images.  
2. Action messages (`topic = 1`), to send a single motor command. 
3. Reset messages (`topic = 2`), to reset the simulation (this only works in simulation - on the real robot if this command is issued, nothing happens).

Neither of these two messages have a response from the robot/sim server. The result of the ping message is that the PC will from now on receive images. The result of the action message is that the robot/sim will start moving. Therefore the ping should always be the first step in establishing a connection from the PC side.

Both messages have to be sent to the IP/hostname of the robot/sim on a `zmq.PUSH` socket via `socket.send_string()`.

You can construct either message by using the method `duckietown_slimremote.networking:construct_action()`.

#### Ping message structure

Each **ping** message has the following format:

    "0 X Y 0"
    
where

    X = PC identifier "ID": random integer in range 
        [0,99999], not zero-buffered.
        This value is randomly chosen by the PC 
        upon initiating the connection. There is currently no
        big importance to this number but it can
        be used to identify concurrent connections
        from the same host.
    Y = IP address of the PC - currently IPv4.
    
    The leading "0" indicates that this is a ping message
    The trailing "0" indicates that this message doesn't
    have an action payload (i.e. motor commands).
    
Example:

    "0 1337 192.168.1.15 0"
    

#### Action message structure

Each **action** message has the following format:

    "1 X Y Z"
    
where

    X,Y = same as for ping message
    
    Z =  either just a motor command (two floating point 
    values) or a motor command combined with an LED command 
    (five floating points values). All these floating point 
    values are separated by comma. The motor part is always 
    in range[-1,1] and corresponds to the velocity of the 
    vehicle and the steering angleThe LED part (last 3 
    floats) are in range [0;1] and correspond to the color
    channels red, green, and blue if the use wants to
    include them. 
    
Example:

    "1 1337 192.168.1.15 -0.54,0.333333"
    (doesn't include LED values) means go backwards at half speed and slightly turn left
    
    "1 1337 192.168.1.15 -0.54,0.3,0,0.55,1"
    (which does include LED values, corresponding to
    0 parts red, 0.55 parts green and 1 part blue) 

#### Reset message structure

Each **reset** message has the following format:

    "2 X Y 0"
    
where (same as for ping message)

    X = PC identifier "ID": random integer in range 
        [0,99999], not zero-buffered.
        This value is randomly chosen by the PC 
        upon initiating the connection. There is currently no
        big importance to this number but it can
        be used to identify concurrent connections
        from the same host.
    Y = IP address of the PC - currently IPv4.
    
    The leading "2" indicates that this is a reset message
    The trailing "0" indicates that this message doesn't
    have an action payload (i.e. motor commands).
    
Example:

    "2 1337 192.168.1.15 0"
    


    
#### Images/Observations

On start, the robot process also launches a process that runs independently of the main process, which grabs camera images as fast as possible (~60Hz) in case of the real robot and once after every action in case of the simulation and sends them to all subscribers. The list of subscribers is updated via the main process via incoming ping messages and dead subscribers are removed after 60s inactivity.

After the first subscriber is connected, the robot/sim camera process opens a publisher (`zmq.PUB`) socket which is bound to the broadcast address at port `8902`. This socket is only created upon first connection and then kept in memory for reuse. Even if the last image subscriber drops out, the socket will keep sending images out without blocking. The images are sent to all subscribers simultaneously. (NOTE: We should test if having more than 2 subscribers connected leads to any slowdown)

The image is transmitted in two steps (code provided by the PyZMQ website):
    
 1. JSON-serialized metadata about the image (i.e. size & datatype), sent with the `zmq.SNDMORE` flag.
 2. Binary buffer of the actual image
 
The image dimensions are currently `160 x 120 x 3` (width x height x color channels in RGB order).

## PC side

The PC client has to create a PUSH socket (`zmq.PUSH`) that is bound to the robot/sim's IP/hostname on port `5558`.

On this socket the PC can send messages according to the format specified above (ping & action).

The PC launches a camera subscriber thread that is constantly listening to images on a `zmq.SUB` socket on the IP address or hostname of the robot on port `8902`. The PC subscriber has to set the allowed topics to be `""` (empty) via `socket.setsockopt_string(zmq.SUBSCRIBE, topic)`, otherwise nothing will be received.
 
## Differences between simulated and real robot

- the real robot has auto-breaking motors for safety in case of agent failure, i.e. if there is no action command after 1s, the motors will decelerate over the course of the next 1s following a square easing function (i.e. decelerate slow in the beginning and very strong at the end up to a halt). So in order to keep the robot moving smoothly an action has to received at least every fully second. The simulated robot has no such deceleration.
- the real robot will send images constantly, whereas the simulator will send images only after a simulation step, which in turn only happens after every action command. The PC interface for both the real and simulated robots only return when a new image is received. Therefore real robot's operating frequency is limited by the camera capture frequency (60Hz) and the simulated robot is limited by the time it takes to send an action via PUSH, step the simulation, and receive an image via PULL. The overhead from ZMQ is minimal and it can send up to 8000 string messages per second over WiFi.
- Therefore the simulation is synchronous and the real robot is asynchronous (meaning it is possible for the robot to move without an action command being present). But the real robot can be observed continuously without sending actions.

