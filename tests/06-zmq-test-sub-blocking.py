import time

import zmq

context = zmq.Context()

socket_sub = context.socket(zmq.SUB)
socket_sub.bind("tcp://*:8901")
socket_sub.setsockopt_string(zmq.SUBSCRIBE, "0")
socket_sub.setsockopt_string(zmq.SUBSCRIBE, "2")
socket_sub.setsockopt_string(zmq.SUBSCRIBE, "3")

print("hello this is SUB", time.time())

should_continue = True

while should_continue:
    print("waiting...")
    string = socket_sub.recv_string()
    print("'{}'".format(string))
    topic, messagedata = string.split(" ")
    print("got topic {}, message {}".format(topic, messagedata))

    if int(topic) == 0:
        should_continue = False
