setlocal
docker rm -f pychanlun-schedule-server
docker rmi -f pychanlun-schedule-server
cd %~dp0 && cd ..\..
docker build -f docker\pychanlun-schedule-server\Dockerfile -t pychanlun-schedule-server .
docker run --restart=always -d --name pychanlun-schedule-server --network qa_network -p 18888:5000 pychanlun-schedule-server
endlocal