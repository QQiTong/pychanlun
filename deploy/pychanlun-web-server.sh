#!/bin/bash

name="pychanlun-web-server"

docker rm -f $name
docker rmi -f $name

docker build -f Dockerfile.web -t $name .

docker run --restart=always -d \
    --name $name \
    --network pychanlun-net \
    -p 8080:80 \
    -p 80:80 \
    $name
