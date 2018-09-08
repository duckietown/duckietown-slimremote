import time

import zmq

from duckietown_slimremote.helpers import random_id, get_py_version
from duckietown_slimremote.networking import make_sub_socket, make_pub_socket, construct_action, recv_array, \
    get_ip

print(get_py_version())

context = zmq.Context()

image_sub = make_sub_socket(for_images=True)
action_pub = make_pub_socket("quacksparrow.local")

poller = zmq.Poller()
poller.register(image_sub, zmq.POLLIN)

own_id = random_id()
own_ip = get_ip()
msg = construct_action(own_id, own_ip)

time.sleep(1)  # wait for sock init

print("sending init", msg)
# init
action_pub.send_string(msg)

# during testing the following block took out the JSON header from the first image.
# In other words the hello message arrived too quickly.

# print("sent, now waiting for hi")
## wait for hello
# res = image_sub.recv_string()
# print("got reply:", res)

tests = 1000
timings = 0

start = time.time()

for i in range(tests):

    # print("sending hb again")
    action_pub.send_string(msg)  # this is harmless bc just a heartbeat

    # print("looking for answer")
    socks = dict(poller.poll(5))
    if image_sub in socks and socks[image_sub] == zmq.POLLIN:
        img = recv_array(image_sub)

        timings += time.time() - start
        start = time.time()

diff = timings / tests

print("avg iamges: {}s/{}Hz".format(
    round(diff, 4),
    round(1 / diff, 4)

))
