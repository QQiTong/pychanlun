docker volume create portainer_data
docker rm -f portainer-ce
docker run --name portainer-ce --restart=always --network qanetwork -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce
