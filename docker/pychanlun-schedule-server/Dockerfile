FROM python:3.7.4

WORKDIR /opt/app
COPY . .

ENV PIP_TRUSTED_HOST mirrors.aliyun.com
ENV PIP_INDEX_URL http://mirrors.aliyun.com/pypi/simple

RUN chmod a+x ./prepare.sh && ./prepare.sh
RUN pip install -r requirements.txt

WORKDIR /opt/app

ENV PYTHONUNBUFFERED 1
ENV PYCHANLUN_CONFIG_ENV production

ENV RQDATAC2_CONF=rqdata://license:R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=@rqdatad-pro.ricequant.com:16011

ENTRYPOINT ["python", "-m", "pychanlun.scheduler"]

