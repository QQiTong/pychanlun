FROM python:3.7

RUN mv /etc/apt/sources.list /etc/apt/sourses.list.backup \
    && echo "deb http://mirrors.163.com/debian/ stretch main non-free contrib" >> /etc/apt/sources.list \
	&& echo "deb http://mirrors.163.com/debian/ stretch-updates main non-free contrib" >> /etc/apt/sources.list \
	&& echo "deb http://mirrors.163.com/debian/ stretch-backports main non-free contrib" >> /etc/apt/sources.list \
	&& echo "deb-src http://mirrors.163.com/debian/ stretch main non-free contrib" >> /etc/apt/sources.list \
	&& echo "deb-src http://mirrors.163.com/debian/ stretch-updates main non-free contrib" >> /etc/apt/sources.list \
	&& echo "deb-src http://mirrors.163.com/debian/ stretch-backports main non-free contrib" >> /etc/apt/sources.list \
	&& echo "deb http://mirrors.163.com/debian-security/ stretch/updates main non-free contrib" >> /etc/apt/sources.list \
	&& echo "deb-src http://mirrors.163.com/debian-security/ stretch/updates main non-free contrib" >> /etc/apt/sources.list

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get -y update
RUN apt-get -y install tzdata
RUN dpkg-reconfigure --frontend noninteractive tzdata

WORKDIR /app/pychanlun
COPY . .
RUN mkdir ~/.pip && cp docker/pip.conf ~/.pip/pip.conf

RUN pip3 install -r requirements.txt
RUN pip3 install --extra-index-url https://rquser:ricequant99@py.ricequant.com/simple/ rqdatac
RUN pip install -e .

ENV PYTHONUNBUFFERED=1
ENV RQDATAC2_CONF=rqdata://license:R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=@rqdatad-pro.ricequant.com:16011
ENV PYCHANLUN_MONGO_URL=mongodb://mgdb:27017/pychanlun

EXPOSE 5000

ENTRYPOINT ["pychanlun", "run-api-server"]
