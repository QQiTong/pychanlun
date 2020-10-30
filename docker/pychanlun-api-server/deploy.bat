setlocal
docker rm -f pychanlun-api-server
docker rmi -f pychanlun-api-server
cd %~dp0 && cd ..\..
docker build -f docker\pychanlun-api-server\Dockerfile -t pychanlun-api-server .
docker run --restart=always -d --name pychanlun-api-server --network qa_network -p 18888:5000 pychanlun-api-server
endlocal