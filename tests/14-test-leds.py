from duckietown_slimremote.pc.robot import RemoteRobot

robot = RemoteRobot("10.204.6.223")  # currently in the lab, can't use zeroconf/avahi

# for i in range(5):
#     robot.step(action=[0, 0, 1, 0, 0])
#     time.sleep(0.5)
#     robot.step(action=[0, 0, 0, 1, 0])
#     time.sleep(0.5)
#     robot.step(action=[0, 0, 0, 0, 1])
#     time.sleep(0.5)

robot.step([0] * 5)
