import time

import numpy as np

from duckietown_slimremote.helpers import random_id, timer
from duckietown_slimremote.networking import get_ip, construct_action, make_push_socket

robot_sock = make_push_socket("quacksparrow.local")

own_id = random_id()
own_ip = get_ip()
msg = construct_action(own_id, own_ip)

# print("sending init", msg)
# robot_sock.send_string(msg)


timings = []
start = time.time()

while True:
    action = np.random.uniform(-1, 1, 2)
    msg = construct_action(own_id, own_ip, action)
    robot_sock.send_string(msg)
    timings, start = timer(timings, start, prefix="action")
    time.sleep(0.01)  # not necessary anymore

# msg = construct_action(own_id, own_ip, (0.5,-0.5))
# robot_sock.send_string(msg)
