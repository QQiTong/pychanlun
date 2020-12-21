docker rm -f gogs
docker run -d --name=gogs --restart=always --network qanetwork -v /opt/gogs:/data gogs/gogs
