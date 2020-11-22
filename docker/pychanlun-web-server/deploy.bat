setlocal
docker rm -f pychanlun-web-server
docker rmi -f pychanlun-web-server
cd %~dp0 && cd ..\..
docker build -f docker\pychanlun-web-server\Dockerfile -t pychanlun-web-server .
docker run --restart=always -d --name pychanlun-web-server --network qanetwork pychanlun-web-server
endlocal
