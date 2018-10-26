import matplotlib

matplotlib.use('TkAgg')  # needed for tkinter GUI
from duckietown_slimremote.helpers import random_id
from duckietown_slimremote.networking import get_ip, construct_action, make_push_socket
from duckietown_slimremote.pc.camera import SubCameraMaster, cam_windows_init_opencv, cam_windows_update_opencv
import numpy as np

host = "quacksparrow.local"

robot_sock = make_push_socket(host)
shape = (120, 160, 3)
dtype = np.uint8
cam = SubCameraMaster(host, shape, dtype)

own_id = random_id()
own_ip = get_ip()
msg = construct_action(own_id, own_ip)

print("sending init", msg)
robot_sock.send_string(msg)

cam_windows_init_opencv()

while True:
    img = cam.get_img_blocking()
    cam_windows_update_opencv(img)
