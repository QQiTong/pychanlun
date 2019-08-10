#!/bin/bash

name="pychanlun"

docker rm -f $name
docker rmi -f $name

docker build -f Dockerfile.back -t $name .
docker run --restart=always -d \
    --name $name \
    --network pychanlun-net
    -p 5000:5000 \
    $name