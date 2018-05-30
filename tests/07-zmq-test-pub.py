import random
import time

import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect("tcp://localhost:8901")
publisher_id = random.randrange(0,99999)

for reqnum in range(20):
    topic = random.randrange(0,5)
    messagedata = "server#{}".format(publisher_id)
    print ("trying to send",messagedata)
    socket.send_string("{} {}".format(topic, messagedata))
    print("sent")

    time.sleep(1)