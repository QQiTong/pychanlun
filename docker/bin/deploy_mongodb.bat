docker rm -f mongodb
docker run --restart=always -d --name mongodb --network qanetwork -m 2g --memory-swap -1 -p 27017:27017 -v qamg:/data/db mongo:bionic
