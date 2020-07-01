rem 创建网路
docker network create -d bridge --subnet 172.11.0.0/24 --gateway 172.11.0.1 qa_network
rem 创建数据卷
docker volume create mongodb
