import time

from Adafruit_MotorHAT import Adafruit_MotorHAT

speeds = {
    "min_speed": 60,
    "max_speed": 255,
    "zero": 0
}
motorhat = Adafruit_MotorHAT(addr=0x60)
leftMotor = motorhat.getMotor(1)
rightMotor = motorhat.getMotor(2)



def run_test(direction, speed):
    leftMotor.setSpeed(speeds[speed])
    leftMotor.run(direction)
    rightMotor.setSpeed(speeds[speed])
    rightMotor.run(direction)


tests = 1000

timings = 0

for i in range(tests):
    start = time.time()
    run_test(Adafruit_MotorHAT.BACKWARD, "min_speed")
    timings += time.time() - start

dt = timings/tests

print("just setting backward and min_speed: ~{}s / ~{}HZ".format(
    round(dt,4),
    round(1/dt,4)
))

########

timings = 0

for i in range(tests):
    start = time.time()
    run_test(Adafruit_MotorHAT.BACKWARD, "max_speed")
    timings += time.time() - start

dt = timings/tests

print("just setting backward and max_speed: ~{}s / ~{}HZ".format(
    round(dt,4),
    round(1/dt,4)
))

########

timings = 0

for i in range(tests):
    start = time.time()
    run_test(Adafruit_MotorHAT.FORWARD, "min_speed")
    timings += time.time() - start

dt = timings/tests

print("just setting forward and min_speed: ~{}s / ~{}HZ".format(
    round(dt,4),
    round(1/dt,4)
))

########

timings = 0

for i in range(tests):
    start = time.time()
    run_test(Adafruit_MotorHAT.FORWARD, "max_speed")
    timings += time.time() - start

dt = timings/tests

print("just setting forward and max_speed: ~{}s / ~{}HZ".format(
    round(dt,4),
    round(1/dt,4)
))


########

timings = 0

for i in range(tests):
    start = time.time()
    run_test(Adafruit_MotorHAT.RELEASE, "zero")
    timings += time.time() - start

dt = timings/tests

print("just setting release: ~{}s / ~{}HZ".format(
    round(dt,4),
    round(1/dt,4)
))

########

timings = 0

for i in range(tests):
    start = time.time()
    run_test(Adafruit_MotorHAT.BACKWARD, "min_speed")
    run_test(Adafruit_MotorHAT.BACKWARD, "max_speed")
    timings += time.time() - start

dt = timings/tests

print("switching between speeds: ~{}s / ~{}HZ".format(
    round(dt,4),
    round(1/dt,4)
))

########

timings = 0

for i in range(tests):
    start = time.time()
    run_test(Adafruit_MotorHAT.FORWARD, "min_speed")
    run_test(Adafruit_MotorHAT.BACKWARD, "min_speed")
    timings += time.time() - start

dt = timings/tests

print("reversing directions: ~{}s / ~{}HZ".format(
    round(dt,4),
    round(1/dt,4)
))


########

timings = 0

for i in range(tests):
    start = time.time()
    run_test(Adafruit_MotorHAT.FORWARD, "min_speed")
    run_test(Adafruit_MotorHAT.BACKWARD, "max_speed")
    timings += time.time() - start

dt = timings/tests

print("reversing directions and changing speeds: ~{}s / ~{}HZ".format(
    round(dt,4),
    round(1/dt,4)
))


run_test(Adafruit_MotorHAT.RELEASE, "zero")



#### RESULTS

# just setting backward and min_speed: ~0.0142s / ~70.3207HZ
# just setting backward and max_speed: ~0.0146s / ~68.7095HZ
# just setting forward and min_speed: ~0.0145s / ~68.7869HZ
# just setting forward and max_speed: ~0.0146s / ~68.677HZ
# just setting release: ~0.0145s / ~68.9242HZ
# switching between speeds: ~0.0289s / ~34.6149HZ
# reversing directions: ~0.029s / ~34.4816HZ
# reversing directions and changing speeds: ~0.0291s / ~34.3723HZ