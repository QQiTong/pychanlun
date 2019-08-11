#!/bin/bash

name="pychanlun-api-server"

docker rm -f $name
docker rmi -f $name

docker build -f Dockerfile.api -t $name .
docker run --restart=always -d \
    --name $name \
    --network pychanlun-net \
    -p 5000:5000 \
    $name