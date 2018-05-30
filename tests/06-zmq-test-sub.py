import time

import zmq

context = zmq.Context()

socket_sub = context.socket(zmq.SUB)
socket_sub.bind("tcp://*:8901")
socket_sub.setsockopt_string(zmq.SUBSCRIBE, "0")
socket_sub.setsockopt_string(zmq.SUBSCRIBE, "2")
socket_sub.setsockopt_string(zmq.SUBSCRIBE, "3")

poller = zmq.Poller()
poller.register(socket_sub, zmq.POLLIN)

print("hello this is SUB", time.time())

should_continue = True
timer = 1000
i = 0
timings = 0

while should_continue:
    start = time.time()
    socks = dict(poller.poll(5))
    if socket_sub in socks and socks[socket_sub] == zmq.POLLIN:
        string = socket_sub.recv_string()
        topic, messagedata = string.split(" ")
        print("got topic {}, message {}".format(topic, messagedata))

        if topic == 0:
            should_continue = False
    timings += time.time() - start

    i += 1
    if i % timer == 0:
        i = 0
        dt = timings / timer
        print("avg poll time is {}s / {}Hz".format(
            round(dt, 4),
            round(1 / dt, 4))
        )
        timings = 0
