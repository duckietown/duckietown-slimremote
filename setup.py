# Adafruit-MotorHAT
import os

from setuptools import setup

IS_RPI = False
rpi_model_file = "/sys/firmware/devicetree/base/model"
if os.path.isfile(rpi_model_file):
    with open(rpi_model_file) as f:
        identifier = f.readline()
        if "Raspberry" in identifier:
            IS_RPI = True

install_requires = [
    'numpy',
    'pillow',
    'pyzmq',
]

if IS_RPI:
    install_requires.append('Adafruit-MotorHAT')  # for controlling the motors
    # install_requires.append('cv2')  # for high speed image capturing

setup(
    name='duckietown_slimremote',
    version='2018.10.1',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'duckietown-start-robot2=duckietown_slimremote.robot.server2:main',
            'duckietown-start-robot=duckietown_slimremote.robot.server:main',
            'duckietown-stop-robot=duckietown_slimremote.robot.server:stop'
        ],
    },
    options={
        'build_scripts': {
            'executable': 'python3',
        },
    }
)
