docker rm -f trilium
docker run -d --name=trilium --restart=always --network qanetwork -v /opt/trilium:/root/trilium-data zadam/trilium
