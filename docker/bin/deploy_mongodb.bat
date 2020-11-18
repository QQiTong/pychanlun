docker rm -f mongodb
docker run --restart=always -d --name mongodb --network qa_network -m 2g --memory-swap -1 -p 27017:27017 -v mongodb:/data/db mongo:bionic
