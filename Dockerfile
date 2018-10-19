FROM resin/raspberrypi3-python:3.6-slim

ENV QEMU_EXECVE 1
ENV DISPLAY :0
EXPOSE 5558 8902

RUN [ "cross-build-start" ]

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python-dev \
        build-essential && \
    apt install -y --no-install-recommends libpng12-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install numpy cython

RUN pip install --index-url https://www.piwheels.org/simple \
    opencv-contrib-python \
    Adafruit-MotorHAT \
    opencv-python \
    pyzmq 

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python-opencv \
        libqtgui4 \
        libjpeg62 \
        libwebp-dev \
        libqt4-test \
        libtiff5-dev \
        libjasper-dev \
        libilmbase-dev \
        libfreetype6-dev \
        libgstreamer1.0-dev \
        libc6 \
        libatlas-base-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR duckietown-slimremote

COPY . .

RUN pip install -e .

RUN [ "cross-build-end" ]


CMD ["duckietown-start-robot2"]
