## Communication Guideline

Robot/Sim side

**IMPORTANT:** The real robot will rapidly decelerate automatically over the course of a second starting from the last action. So if actions keep on coming, the speed keeps up, but if actions ever lag behind, the robot will slow down to a halt. This slow-down behavior doesn't exist in simulation.
The low level robot controller runs in its own thread to decelerate automatically if no signals come in.

```python
# require MAX_WAIT in seconds
# (MAX_WAIT is the period,
#  i.e. the inverse of the comm frequency)

# require ROBOT which is the robot/sim low level
# controller that takes a
# list of two floats in [-1;1]

socket_sub = make_sub_socket()
sockets_pub = []

# controller queue to give priority
controllers = []

# action queue bc multiple actions could be received
actions = []
start = current_time()

while True:

  # wait for any controller to send
  # their unique ID+IP and action
  controller_id, data = socket.receive() # blocking

  if controller_id not in controllers:
    controller.append(controller_id)

    # create new publisher socket for this controller
    # which is where we send the observations later
    sock_pub = make_pub_socket(controller_id)

    # be polite
    sock_pub.send("welcome to the duckie party")

    # add this controller to the list of sockets
    # which are interested in this robot
    sockets_pub.append(sock_pub)


  actions.append((data,controller_id))
  time_passed = current_time - start

  if time_passed >= MAX_WAIT:
    # go over the list of actions and pick out the one
    # that came from the latest-joined controller
    action = select_action(actions, controllers)

    ROBOT.run(action)
    observation = ROBOT.observe()

    for sock_pub in sockets_pub:
      sock_pub.send(observation) # non-blocking

    actions = []
    start = current_time()

    # this function removes controllers from the list
    # which haven't sent something in N cycles, so that
    # after hours of running the controller list
    # doesn't overflow
    controller_clearing_magic(controllers)
```
