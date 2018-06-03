from queue import Queue

from duckietown_slimremote.networking import make_pull_socket, has_pull_message, receive_data
from duckietown_slimremote.robot.camera import ThreadedPubCamera

# start camera thread
# start motor thread
# start subscriber sub

cam_queue = Queue()
cam = ThreadedPubCamera(cam_queue)
cam.daemon = True # so that you can kill the thread
cam.start()

sock, poll = make_pull_socket()

cam_subscribers = []

# main loop, look for new incoming connections

print("Robot listening to incoming connections...")

while True:
    if has_pull_message(sock, poll):
        success, data = receive_data(sock)
        if not success:
            print(data)  # in error case, this will contain the err msg
            continue
        if data["ip"] not in cam_subscribers:
            cam_queue.put(data["ip"])
            cam_subscribers.append(data["ip"])
        print("received new connection:", data)
