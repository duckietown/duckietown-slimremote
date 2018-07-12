# stretch because that's the same as the hypriotOS image
FROM  resin/rpi-raspbian:stretch

RUN [ "cross-build-start" ]

# build deps
RUN apt-get update && \
    apt-get install --no-install-recommends -y build-essential git wget cmake pkg-config \
    libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev \
    libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev \
    libx264-dev libatlas-base-dev gfortran python3-dev

RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py

ADD https://github.com/opencv/opencv/archive/3.4.1.tar.gz opencv.tar.gz
RUN tar -xvzf opencv.tar.gz && mv opencv-3.4.1 opencv

ADD https://github.com/opencv/opencv_contrib/archive/3.4.1.tar.gz opencv_contrib.tar.gz
RUN tar -xvzf opencv_contrib.tar.gz && mv opencv_contrib-3.4.1 opencv_contrib

RUN cd opencv && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
          -D CMAKE_INSTALL_PREFIX=/usr/local \
          -D INSTALL_C_EXAMPLES=OFF \
          -D BUILD_PERF_TESTS=OFF \
          -D BUILD_TESTS=OFF \
          -D INSTALL_PYTHON_EXAMPLES=OFF \
          -D OPENCV_EXTRA_MODULES_PATH=/opencv_contrib/modules \
          -D BUILD_EXAMPLES=OFF .. && \
    make -j4 && \
    make install && \
    ldconfig

# cleanup
RUN rm -rf ~/opencv && \
    rm -rf ~/opencv_contrib && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get remove libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev \
    libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev \
    libx264-dev libatlas-base-dev python3-dev

RUN git clone --depth 1 https://github.com/duckietown/duckietown-slimremote.git && \
    cd duckietown-slimremote && \
    pip3 install -e .

RUN [ "cross-build-end" ]

EXPOSE 5558 8902

CMD ["duckietown-start-robot2"]
