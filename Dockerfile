FROM duckietown/slimremote-base:latest

WORKDIR duckietown-slimremote

COPY . .

RUN pip3 install -e .

RUN [ "cross-build-end" ]


CMD ["duckietown-start-robot2"]
