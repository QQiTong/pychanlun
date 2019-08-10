#!/bin/bash

name="pychanlun"

docker rm -f $name
docker rmi -f $name

docker build -t $name ./dist
docker run --restart=always -d \
    --name $name \
    --expose 5000 \
    $name