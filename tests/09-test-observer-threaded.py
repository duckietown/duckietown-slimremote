from duckietown_slimremote.networking import make_sub_socket, make_pub_socket, construct_action, recv_array, \
    get_ip, ThreadedImageSubscriber, start_thread_w_queue
import time

import zmq

from duckietown_slimremote.helpers import random_id, get_py_version

print(get_py_version())

image_queue = start_thread_w_queue(ThreadedImageSubscriber)
action_pub = make_pub_socket("quacksparrow.local")

own_id = random_id()
own_ip = get_ip()
msg = construct_action(own_id, own_ip)

time.sleep(1)  # wait for sock init

print("sending init", msg)
# init
action_pub.send_string(msg)
#
# during testing the following block took out the JSON header from the first image.
# In other words the hello message arrived too quickly.

# print("sent, now waiting for hi")
## wait for hello
# res = image_sub.recv_string()
# print("got reply:", res)

tests = 100
timings = 0
success = 0
start = time.time()

while True:

    action_pub.send_string(msg)  # this is harmless bc just a heartbeat

    if not image_queue.empty():
        img = image_queue.get()
        success += 1
        timings += time.time() - start
        start = time.time()
        if success >= tests:
            break

diff = timings / tests

print("avg images: {}s/{}Hz".format(
    round(diff, 4),
    round(1 / diff, 4)
))
