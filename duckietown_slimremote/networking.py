from __future__ import unicode_literals
from builtins import dict, str
import ast
from queue import Queue
from threading import Thread

import zmq

import sys

if sys.version_info > (3,):
    buffer = memoryview

import numpy as np

import socket

hostname = socket.gethostname()

context = zmq.Context()  # we only ever need one context. This is thread-safe, but not process-safe afaik

RESET = "reset"

def get_port(for_images=False):
    port = 8901  # for pc->robot comm
    if for_images:
        port = 8902  # for robot->spc comm
    return port


def get_host():
    return hostname


def get_ip():
    return socket.gethostbyname(hostname)


def make_sub_socket(with_failsafe=False, for_images=False, context_=None, target=None):
    if context_ is None:
        context_ = context
    if target is None:
        target = "*"

    port = get_port(for_images)

    print("starting sub socket on", port)
    socket_sub = context_.socket(zmq.SUB)
    socket_sub.connect("tcp://{}:{}".format(target, port))

    if not for_images:
        print("listening for topics 0, 1")
        socket_sub.setsockopt_string(zmq.SUBSCRIBE, "0")
        socket_sub.setsockopt_string(zmq.SUBSCRIBE, "1")
        if with_failsafe:
            print("...and 99")
            socket_sub.setsockopt_string(zmq.SUBSCRIBE, "99")

    else:  # subscribe to messags without topic
        socket_sub.setsockopt_string(zmq.SUBSCRIBE, "")

    return socket_sub


def make_pub_socket(for_images=False, context_=None):
    if context_ is None:
        context_ = context

    port = get_port(for_images)

    print("starting pub socket on", port)
    socket_pub = context_.socket(zmq.PUB)
    socket_pub.bind("tcp://*:{}".format(
        port
    ))

    return socket_pub


def make_pull_socket(with_poller=True):
    socket_pull = context.socket(zmq.PULL)
    socket_pull.bind("tcp://*:5558")
    poller = None
    if with_poller:
        poller = zmq.Poller()
        poller.register(socket_pull, zmq.POLLIN)

    return (socket_pull, poller)


def has_pull_message(socket_pull, poller, timeout=5):
    socks = dict(poller.poll(timeout))
    if socket_pull in socks and socks[socket_pull] == zmq.POLLIN:
        return True
    else:
        return False


def make_push_socket(ip, context_=None):
    if context_ is None:
        context_ = context

    socket_push = context_.socket(zmq.PUSH)
    socket_push.connect("tcp://{}:5558".format(ip))

    return socket_push


def receive_data(socket_sub):
    data = socket_sub.recv_string()
    split = data.split(" ")

    if len(split) != 4:
        data = "Received data of wrong length." \
               "The data must have this format:" \
               "'W X Y Z', where \n" \
               "W is an integer (the topic, i.e. 0, 1 or 2),\n" \
               "X is a a random integer between 0 and 99999 to " \
               "identify the client (e.g. 45678,\n" \
               "Y is the IP address (e.g. 10.0.0.1),\n" \
               "Z is the action (e.g. for topic 0: -1,1 " \
               "[if you don't want LED control] or -1,1,0,0.5,0 " \
               "[if you want LED control] or for topic 1: 0).\n" \
               "Example: '0 3716 192.168.0.14 0.5,0.6'.\n" \
               "What I got from you was: '{}'".format(data)
        return False, data

    topic = int(split[0])  # topic 0 means set action, topic 1 means get image, topic 2 means reset
    id = split[1]  # TODO: add ID sanity check here
    ip = split[2]  # TODO: add IP sanity check here
    msg = split[3]

    if topic not in [0, 1, 2, 99]:
        data = "Received an incorrect topic: {}." \
               "Only allowed topics: 0, 1 or 2.".format(topic)
        return False, data

    if topic == 0:
        msg = msg.split(",")
        if len(msg) != 2 and len(msg) != 5:
            msg = msg[0].split(";")
            if len(msg) != 2 and len(msg) != 5:
                data = "The action command is malformed: '{}'." \
                       "The action must be either two or five floating point" \
                       "values separated by a comma like so: " \
                       "0.5111,-0.7 or so 0.5111,-0.7,0,0.5,1".format(msg)
                return False, data

        msg = [float(m) for m in msg]

        ### check for LED command sanity
        if len(msg) == 5:
            if min(msg[2:]) < 0 or max(msg[2:]) > 1:
                data = "The LED command has to be in range [0;1] " \
                       "on each RGB color channel. However I got the " \
                       "colors: {}".format(msg)
                return False, data

    return True, {"topic": topic, "id": id, "ip": ip, "msg": msg}


def say_hi(socket_pub):
    socket_pub.send_string("{} {}".format(
        0,  # the topic for general messages
        "welcome to the duckie party"
    ))


def send_array(socket, nparray, flags=0, copy=True, track=False):
    """send a numpy array with metadata
    from http://pyzmq.readthedocs.io/en/latest/serialization.html
    """
    md = dict(
        dtype=str(nparray.dtype),
        shape=nparray.shape,
    )
    socket.send_json(md, flags | zmq.SNDMORE)
    return socket.send(nparray, flags, copy=copy, track=track)


def recv_array(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = buffer(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])


def send_gym(socket, img, reward, done, misc=None, flags=0, copy=True, track=False):
    if misc is None:
        misc = {"challenge": None}

    send_array(socket, img, flags | zmq.SNDMORE, copy, track)
    socket.send_string(str(reward), flags | zmq.SNDMORE)
    socket.send_string(str(done), flags | zmq.SNDMORE)
    return socket.send_string(str(misc), flags)


def recv_gym(socket, flags=0, copy=True, track=False):
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    rew = float(socket.recv_string(flags=flags))

    done = socket.recv_string(flags=flags)
    done = (done == "True")

    misc = socket.recv_string(flags=flags)
    misc = ast.literal_eval(misc)

    buf = buffer(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return (A.reshape(md['shape']), rew, done, misc)


def construct_action(id, ip=None, action=None):
    # if id is None:
    #     id = random_id()

    if ip is None:
        ip = get_ip()

    if action is None:  # then it's a heartbeat
        return "1 {} {} 0".format(id, ip)
    elif isinstance(action, str) and action == RESET:
        return "2 {} {} 0".format(id, ip)
    else:
        assert len(action) == 2 or len(action) == 5
        out = "0 {} {} ".format(id, ip)
        if len(action) == 2:
            return out + "{},{}".format(*action)
        else:
            return out + "{},{},{},{},{}".format(*action)


class ThreadedActionSubscriber(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        context = zmq.Context()
        self.sub = make_sub_socket(with_failsafe=True, context_=context)
        print("started action subscriber thread")

    def run(self):
        keep_running = True
        while keep_running:
            success, data = receive_data(self.sub)
            if not success:
                print(data)  # in error case, this will contain the err msg
                continue
            self.queue.put(data)


class ThreadedImageSubscriber(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        context = zmq.Context()
        self.sub = make_sub_socket(for_images=True, context_=context)
        print("started image subscriber thread")

    def run(self):
        keep_running = True
        while keep_running:
            img = recv_array(self.sub)
            self.queue.put(img)


def start_thread_w_queue(threadName):
    queue = Queue()
    sub_thread = threadName(queue)
    sub_thread.daemon = True  # so that program can exist without waiting for thread
    sub_thread.start()
    return queue  # this is all we care about


def get_last_queue_element(queue):
    # it turns out there is also a thing called LifoQueue...
    out = queue.get(block=True)
    while not queue.empty():
        out = queue.get()
    return out
