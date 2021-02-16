docker rm -f gogs
docker run -d --name=gogs --restart=always --network qanetwork -p 3000:3000 -v gogs_data:/data gogs/gogs
