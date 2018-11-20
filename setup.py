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
    'future',
]

if IS_RPI:
    install_requires.append('Adafruit-MotorHAT')  # for controlling the motors
    install_requires.append('picamera')
    # install_requires.append('cv2')  # for high speed image capturing


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename='duckietown_slimremote/__init__.py')


setup(
    name='duckietown_slimremote',
    version=version,
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
