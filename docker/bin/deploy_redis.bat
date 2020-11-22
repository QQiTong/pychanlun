docker rm -f redis
docker run --restart=always -d --name redis --network qanetwork -p 6379:6379 -v redis:/data redis
