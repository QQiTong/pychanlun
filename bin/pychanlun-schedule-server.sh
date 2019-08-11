#!/bin/bash

name="pychanlun-schedule-server"

docker rm -f $name
docker rmi -f $name

docker build -f Dockerfile.schedule -t $name .
docker run --restart=always -d \
    --name $name \
    --network pychanlun-net \
    $name