#!/bin/bash

docker rm -f mongodb
docker run --restart=always -d --name mongodb --network qa_network -p 27017:27017 -v /data/mongo:/data/db mongo:bionic
