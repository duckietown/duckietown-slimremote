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


def dir2text(direction):
    if direction == Adafruit_MotorHAT.FORWARD:
        return "forward"
    elif direction == Adafruit_MotorHAT.BACKWARD:
        return "backward"
    else:
        return "release"


def run_test(direction, speed):
    leftMotor.setSpeed(speeds[speed])
    leftMotor.run(direction)
    rightMotor.setSpeed(speeds[speed])
    rightMotor.run(direction)

    print(speed, dir2text(direction))

    for i in range(3):
        time.sleep(1)
        pass  # do nothing... robot keeps running


run_test(Adafruit_MotorHAT.FORWARD, "min_speed")
run_test(Adafruit_MotorHAT.FORWARD, "max_speed")

run_test(Adafruit_MotorHAT.BACKWARD, "min_speed")
run_test(Adafruit_MotorHAT.BACKWARD, "max_speed")

run_test(Adafruit_MotorHAT.RELEASE, "max_speed")
run_test(Adafruit_MotorHAT.RELEASE, "zero")
