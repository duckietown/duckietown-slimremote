FROM duckietown/slimremote-base

RUN [ "cross-build-start" ]

RUN git clone https://github.com/duckietown/duckietown-slimremote.git && \
    cd duckietown-slimremote && \
    pip3 install -e .

RUN [ "cross-build-end" ]

EXPOSE 5558 8902

CMD ["duckietown-start-robot2"]
