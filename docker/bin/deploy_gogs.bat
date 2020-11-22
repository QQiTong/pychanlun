docker rm -f gogs
docker run -d --name=gogs --restart=always --network qanetwork -v D:\gogs:/data gogs/gogs
