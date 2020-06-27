#!/usr/bin/env bash

ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
export DEBIAN_FRONTEND=noninteractive
apt-get install -y tzdata
dpkg-reconfigure --frontend noninteractive tzdata

python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip setuptools wheel

tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make -j
make install

python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple numpy
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple TA-Lib

pip install --extra-index-url https://rquser:ricequant99@py.ricequant.com/simple/ rqdatac
