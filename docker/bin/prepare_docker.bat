docker network create -d bridge --subnet 172.19.0.0/24 --gateway 172.19.0.1 qanetwork
docker volume create qamg
docker volume create qacode
docker volume create portainer_data
