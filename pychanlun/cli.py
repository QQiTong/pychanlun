# -*- coding: utf-8 -*-

import os, sys

import logging
import click
from pychanlun import server as apiserver
from pychanlun.monitor import BeichiMonitor, stock_signal_calculator
from pychanlun.market_data import tdx_local_downloader, global_futures_downloader
from pychanlun.monitor import stock as stock_monitoring


@click.group()
def run():
    pass


"""
运行api服务器
pychanlun server run
"""


@run.command()
@click.argument("command", default="run")
@click.option('--port', type=int, default=5000)
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
下载外盘数据
pychanlun global-futures download
"""


@run.command()
@click.argument("name", default="download")
def global_futures(**kwargs):
    name = kwargs.get("name")
    if name == "download":
        global_futures_downloader.run(**kwargs)


@run.command()
@click.option('--source', type=str, default="tdxlocal")
@click.option('--days', type=int, default=7)
@click.option('--code', type=str)
@click.option('--period', type=str)
def download_stock_data(**kwargs):
    source = kwargs.get("source")
    if source == "tdxlocal":
        logging.info("从通达信下载股票数据 开始")
        tdx_local_downloader.run(**kwargs)
        logging.info("从通达信下载股票数据 完成")


@run.command()
@click.option('--code', type=str)
@click.option('--period', type=str)
def calculate_stock_signal(**kwargs):
    logging.info("股票信号计算 开始")
    stock_signal_calculator.run(**kwargs)
    logging.info("股票信号计算 结束")


@run.command()
@click.option('--code', type=str)
@click.option('--period', type=str)
def monitoring_stock(**kwargs):
    logging.info("股票监控 开始")
    stock_monitoring.run(**kwargs)
    logging.info("股票监控 结束")


if __name__ == '__main__':
    run()
