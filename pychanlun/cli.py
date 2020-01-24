# -*- coding: utf-8 -*-

import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import click
from pychanlun import server as apiserver
from pychanlun.monitor import BeichiMonitor
import logging
from pychanlun.market_data import tdx_local_downloader, stock_signal_calculator


@click.group()
def run():
    pass


"""
运行api服务器
pychanlun server run
"""
@run.command()
@click.argument("command", default="run")
def server(**kwargs):
    """运行服务端"""
    command = kwargs.get('command')
    if command == "run":
        apiserver.run(**kwargs)

"""
运行背驰监控程序
pychanlun monitor beichi
"""
@run.command()
@click.argument("name", default="beichi")
def monitor(**kwargs):
    """运行监控"""
    name = kwargs.get("name")
    if name == "beichi":
        BeichiMonitor.run(**kwargs)


"""
从通达信软件的本地文件下载股票数据:
pychanlun stock download --source tdxlocal
从下载好的数据计算笔、段、中枢和信号:
pychanlun stock calculate
"""
@run.command()
@click.argument("command", default="download")
@click.option('--source', type=str, default="tdxlocal")
@click.option('--days', type=int, default=7)
def stock(**kwargs):
    logger = logging.getLogger()
    command = kwargs.get("command")
    if command == "download":
        source = kwargs.get("source")
        if source == "tdxlocal":
            logger.info("从通达信下载股票数据 开始")
            tdx_local_downloader.run(**kwargs)
            logger.info("从通达信下载股票数据 完成")
    elif command == "calculate":
        logger.info("股票信号计算 开始")
        stock_signal_calculator.run(**kwargs)
        logger.info("股票信号计算 结束")

if __name__ == '__main__':
    run()
