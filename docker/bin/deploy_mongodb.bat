docker rm -f mongodb
docker run --restart=always -d --name mongodb --network qanetwork -p 27017:27017 -v qamg:/data/db mongo:4.4-bionic
