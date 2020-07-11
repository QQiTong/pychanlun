docker rm -f pychanlun-api-server
docker rmi -f pychanlun-api-server

cd %~dp0 && cd ..\..

docker build -f docker\Dockerfile.api -t pychanlun-api-server .

docker run --restart=always -d --name pychanlun-api-server --network qa_network -p 18888:5000 pychanlun-api-server
