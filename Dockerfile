FROM resin/raspberrypi3-python:3.5-slim

ENV QEMU_EXECVE 1
ENV DISPLAY :0
EXPOSE 5558 8902

RUN [ "cross-build-start" ]

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python3-dev \
        build-essential && \
    apt install -y --no-install-recommends libpng12-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install numpy Cython

RUN pip3 install Adafruit-MotorHAT \
    pyzmq

RUN pip3 install future

RUN pip install --index-url https://www.piwheels.org/simple \
    picamera pillow

RUN apt-get update -y && apt-get install -y python3-tk wget tk-dev tk tcl-dev tcl

RUN wget "https://github.com/jabelone/OpenCV-for-Pi/raw/master/latest-OpenCV.deb" && dpkg -i latest-OpenCV.deb

#RUN pip install --index-url https://www.piwheels.org/simple \
#    opencv-python


#RUN apt-get update -y && \
#    apt-get install -y --no-install-recommends \
#        libqtgui4 \
#        libjpeg62 \
#        libwebp-dev \
#        libqt4-test \
#        libtiff5-dev \
#        libjasper-dev \
#        libilmbase-dev \
#        libfreetype6-dev \
#        libgstreamer1.0-dev \
#        libc6 \
#        libatlas-base-dev && \
#    rm -rf /var/lib/apt/lists/*

WORKDIR duckietown-slimremote

COPY . .

RUN pip3 install -e .

RUN [ "cross-build-end" ]


CMD ["duckietown-start-robot2"]
