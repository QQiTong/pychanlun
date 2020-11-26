docker rm -f trilium
docker run -d --name=trilium --restart=always --network qanetwork -v D:\trilium:/root/trilium-data zadam/trilium
