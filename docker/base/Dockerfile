# stretch because that's the same as the hypriotOS image
FROM  resin/rpi-raspbian:stretch

COPY ./bin/ /usr/bin/

RUN [ "cross-build-start" ]

RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential git wget cmake pkg-config \
    libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev \
    libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev \
    libx264-dev libatlas-base-dev gfortran python3-dev && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py && \
    pip3 install numpy Adafruit-MotorHAT && \
    cd ~ && \
    git clone https://github.com/Itseez/opencv.git && \
    cd opencv && \
    git checkout 3.4.1 && \
    cd ~ && \
    git clone https://github.com/Itseez/opencv_contrib.git && \
    cd opencv_contrib && \
    git checkout 3.4.1 && \
    cd ~/opencv && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
         -D CMAKE_INSTALL_PREFIX=/usr/local \
         -D INSTALL_C_EXAMPLES=OFF \
         -D INSTALL_PYTHON_EXAMPLES=OFF \
         -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
         -D BUILD_EXAMPLES=OFF .. && \
    make -j4 && \
    make install && \
    ldconfig && \
    rm -rf ~/opencv && \
    rm -rf ~/opencv_contrib && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get remove libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev \
    libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev \
    libx264-dev libatlas-base-dev python3-dev

RUN [ "cross-build-end" ]
