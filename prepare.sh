#!/usr/bin/env bash

python -m pip install --upgrade pip setuptools wheel

pushd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
python -m pip install TA-Lib
popd
