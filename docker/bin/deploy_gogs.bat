docker rm -f gogs
docker run -d --name=gogs --restart=always --network qa_network -v D:\gogs:/data gogs/gogs
