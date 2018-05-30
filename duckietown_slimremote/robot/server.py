import time
from queue import Queue
from duckietown_slimremote.robot.camera import Camera
from duckietown_slimremote.robot.constants import MAX_WAIT, INACTIVE_CLEANUP_TIMER
from duckietown_slimremote.helpers import select_action, remove_inactive, get_py_version
from duckietown_slimremote.robot.motors import Controller, FailsafeController
from duckietown_slimremote.networking import make_pub_socket, send_array, \
    ThreadedActionSubscriber, start_thread_w_queue, get_last_queue_element
import numpy as np
print(get_py_version())


def stop():
    ctrl = Controller()
    ctrl.stop()

def main():
    print("Launching Duckie Slimremote Robot Server...")
    # require MAX_WAIT in seconds
    # (MAX_WAIT is the period,
    #  i.e. the inverse of the comm frequency)

    robot = FailsafeController()
    cam = Camera()


    subscriber_queue = start_thread_w_queue(ThreadedActionSubscriber)
    sockets_pub = []

    # controller queue to give priority
    controllers = []

    # action queue bc multiple actions could be received
    actions = []
    start = time.time()

    # logbook for keeping track when a controller goes dark
    # logs format: (time.time(), controller_id, topic, action)
    logs = []

    counter = 0

    timer2 = time.time()
    timer2_tests = 100
    timer2_counter = 0

    timer_msg_total = []
    timer_pub_total = []
    timer_srt_total = []
    timer_obs_total = []
    timer_cln_total = []
    timer_total_counter = 0

    while True:

        # print ("waiting for action")

        timer_msg = time.time()
        data = get_last_queue_element(subscriber_queue)
        timer_msg_total.append(time.time() - timer_msg)

        topic, controller_id, controller_ip, msg = data
        logs.append((time.time(), controller_id, topic, msg))

        if controller_id not in controllers:
            controllers.append(controller_id)

            # create new publisher socket for this controller
            # which is where we send the observations later
            sock_pub = make_pub_socket(controller_ip, for_images=True)

            # be polite
            # HOWEVER DONT RELY ON THIS MESSAGE. IT MIGHT BE DROPPED
            # say_hi(sock_pub)

            # add this controller to the list of sockets
            # which are interested in this robot
            sockets_pub.append((controller_id, sock_pub))

        if topic == 0:
            actions.append((controller_id, msg))

        time_passed = time.time() - start

        # TODO: add dealing with signal 99

        if time_passed >= MAX_WAIT:
            timer_srt = time.time()
            if len(actions) > 0:
                # go over the list of actions and pick out the one
                # that came from the latest-joined controller
                action = select_action(actions, controllers)

                robot.run(action)
            timer_srt_total.append(time.time() - timer_srt)

            timer_obs = time.time()
            observation = cam.observe()
            timer_obs_total.append(time.time()-timer_obs)

            timer_pub = time.time()
            for sock_pub in sockets_pub:
                # non-blocking, i.e. doesn't rely on hosts being alive
                # print ("sending out pic to",sock_pub[0])
                send_array(sock_pub[1], observation)
            timer_pub_total.append(time.time() - timer_pub)

            actions = []
            start = time.time()

            timer2_counter += time.time() - timer2

            if (counter+1) % timer2_tests == 0:
                diff = timer2_counter / timer2_tests
                print("msg speed: {}s/{}Hz".format(
                    round(diff, 4),
                    round(1 / diff, 4),
                ))
                timer2_counter = 0
            timer2 = time.time()

            timer_cln = time.time()
            counter += 1
            if counter == INACTIVE_CLEANUP_TIMER:
                # this function removes controllers from the list
                # which haven't sent something in N cycles, so that
                # after hours of running the controller list
                # doesn't overflow
                remove_inactive(logs, controllers, sockets_pub)
                counter = 0
            timer_cln_total.append(time.time() - timer_cln)
            timer_total_counter += 1

            if timer_total_counter == 50:
                print("msg {}\npub {}\nsrt {}\nobs {}\ncln {}\n".format(
                    np.mean(timer_msg_total),
                    np.mean(timer_pub_total),
                    np.mean(timer_srt_total),
                    np.mean(timer_obs_total),
                    np.mean(timer_cln_total),
                ))
                timer_total_counter = 0


