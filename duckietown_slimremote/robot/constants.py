MOTOR_MAX_SPEED = 255
MOTOR_MIN_SPEED = 60  # currently unused

# what's the max command frequency?
# (this is the inverse of the freq, i.e. the period)
MAX_WAIT = 0.01

# in seconds, how long does it take for the robot's speed to
# go down to zero after receiving the last action command?
DECELERATION_BREAK_TIME = 1

# in seconds, how long after the last action command does the robot
# start decelerating
DECELERATION_TIMEOUT = 1

# related: how many steps in decel?
DECELERATION_STEPS = 100

# Sometimes the Pi camera doesn't return a correct image.
# But if this happens too often, we should cancel the recording and
# inspect the robot. This is the counter for faulty shots
# in a row.
CAM_FAILURE_COUNTER = 10

# Look for clients(observers) who have become inactive every N steps.
# If there was a single activity of a client in this time frame, it will
# not be removed.
INACTIVE_CLEANUP_TIMER = 500
