FROM resin/raspberrypi3-alpine-python:3.4-slim

RUN [ "cross-build-start" ]

RUN pip3 install --index-url https://www.piwheels.org/simple \
    opencv-contrib-python \
    opencv-python \
    pyzmq 

WORKDIR duckietown-slimremote

COPY . .

RUN apk --no-cache add gcc && \
    pip3 install -e . && \
    apk del gcc && \
    rm -rf /var/lib/apt/lists/*

RUN [ "cross-build-end" ]

EXPOSE 5558 8902

CMD ["duckietown-start-robot2"]
