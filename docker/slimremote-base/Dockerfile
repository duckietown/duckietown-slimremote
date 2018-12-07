# This image is called "duckietown/slimremote-base" and was made so
# that changes to the actual slimremote container don't have to recompile the entire image

# If for any reason you think this needs to be changed, you can recompile this with
# docker build -t duckietown/slimremote-base docker/slimremote-base


FROM resin/raspberrypi3-python:3.5-slim

ENV QEMU_EXECVE 1
ENV DISPLAY :0
EXPOSE 5558 8902

RUN [ "cross-build-start" ]

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python3-dev \
        build-essential python3-tk wget tk-dev tk tcl-dev tcl && \
    apt install -y --no-install-recommends libpng12-dev && \
    rm -rf /var/lib/apt/lists/*

RUN wget "https://github.com/jabelone/OpenCV-for-Pi/raw/master/latest-OpenCV.deb" && dpkg -i latest-OpenCV.deb

RUN pip3 install numpy Cython Adafruit-MotorHAT \
    pyzmq future

RUN pip install --index-url https://www.piwheels.org/simple \
    picamera pillow