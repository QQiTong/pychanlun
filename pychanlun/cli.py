# -*- coding: utf-8 -*-

import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import click
from pychanlun import server as apiserver
from pychanlun.monitor import BeichiMonitor
import logging
from pychanlun.market_data import tdx_local_downloader

@click.group()
def run():
    pass

@run.command()
@click.argument("command", default="run")
def server(**kwargs):
    """运行服务端"""
    command = kwargs.get('command')
    if command == "run":
        apiserver.run(**kwargs)

@run.command()
@click.argument("name", default="beichi")
def monitor(**kwargs):
    """运行监控"""
    name = kwargs.get("name")
    if name == "beichi":
        BeichiMonitor.run(**kwargs)

"""
从通达信本地文件下载股票数据: pychanlun stock-data download localtdx
"""
@run.command()
@click.argument("command", default="download")
@click.option('--source', type=str, default="tdxlocal")
def stock_data(**kwargs):
    logger = logging.getLogger()
    command = kwargs.get("command")
    if command == "download":
        source = kwargs.get("source")
        if source == "tdxlocal":
            logger.info("从通达信下载股票数据 开始")
            tdx_local_downloader.run(**kwargs)
            logger.info("从通达信下载股票数据 完成")

if __name__ == '__main__':
    run()
