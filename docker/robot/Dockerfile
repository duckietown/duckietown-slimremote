FROM resin/raspberrypi3-python:3.4

RUN [ "cross-build-start" ]

RUN pip3 install opencv-python opencv-contrib-python --index-url https://www.piwheels.org/simple

COPY . duckietown-slimremote

RUN pip3 install -e duckietown-slimremote/

RUN [ "cross-build-end" ]

EXPOSE 5558 8902

CMD ["duckietown-start-robot2"]
