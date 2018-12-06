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

JOYSTICK_PATH = "/dev/input/js0"

# Joystick check means file system access, and we don't want that too often.
# So we only check every couple cycles.
CHECK_JOYSTICK_EVERY_N = 100

JOYSTICK_AXIS_NAMES = {
    0x00: 'x',
    0x01: 'y',
    0x02: 'z',
    0x03: 'rx',
    0x04: 'ry',
    0x05: 'rz',
    0x06: 'trottle',
    0x07: 'rudder',
    0x08: 'wheel',
    0x09: 'gas',
    0x0a: 'brake',
    0x10: 'hat0x',
    0x11: 'hat0y',
    0x12: 'hat1x',
    0x13: 'hat1y',
    0x14: 'hat2x',
    0x15: 'hat2y',
    0x16: 'hat3x',
    0x17: 'hat3y',
    0x18: 'pressure',
    0x19: 'distance',
    0x1a: 'tilt_x',
    0x1b: 'tilt_y',
    0x1c: 'tool_width',
    0x20: 'volume',
    0x28: 'misc',
}

JOYSTICK_BUTTON_NAMES = {
    0x120: 'trigger',
    0x121: 'thumb',
    0x122: 'thumb2',
    0x123: 'top',
    0x124: 'top2',
    0x125: 'pinkie',
    0x126: 'base',
    0x127: 'base2',
    0x128: 'base3',
    0x129: 'base4',
    0x12a: 'base5',
    0x12b: 'base6',
    0x12f: 'dead',
    0x130: 'a',
    0x131: 'b',
    0x132: 'c',
    0x133: 'x',
    0x134: 'y',
    0x135: 'z',
    0x136: 'tl',
    0x137: 'tr',
    0x138: 'tl2',
    0x139: 'tr2',
    0x13a: 'select',
    0x13b: 'start',
    0x13c: 'mode',
    0x13d: 'thumbl',
    0x13e: 'thumbr',

    0x220: 'dpad_up',
    0x221: 'dpad_down',
    0x222: 'dpad_left',
    0x223: 'dpad_right',

    # XBox 360 controller uses these codes.
    0x2c0: 'dpad_left',
    0x2c1: 'dpad_right',
    0x2c2: 'dpad_up',
    0x2c3: 'dpad_down',
}

IK = {
    "gain": 1.0,
    "trim": 0.0,
    "radius": 0.0318,
    "k": 27.0,
    "limit": 1.0,
    "wheel_dist": 0.102,
    "epsilon": 0.1
}
