#!/bin/bash

name="mongo-server"

docker rm -f $name
docker rmi -f $name

docker run --restart=always -d \
    --name $name \
    --network pychanlun-net \
    -p 27017:27017 \
    -v /data/mongo:/data/db \
    mongo:4.0.11-xenial --auth
