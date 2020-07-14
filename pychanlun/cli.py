# -*- coding: utf-8 -*-

import logging
import click
from pychanlun import server as api_server
from pychanlun.monitor import BeichiMonitor
from pychanlun.select import a_stock_signal
from pychanlun.market_data import tdx_local_downloader, global_futures_downloader
from pychanlun.monitor import a_stock_tdx as stock_monitoring


@click.group()
def run():
    pass


"""
运行api服务器
pychanlun run-api-server
"""


@run.command()
@click.option('--port', type=int, default=5000)
def run_api_server(**kwargs):
    api_server.run(**kwargs)


"""
运行背驰监控程序
pychanlun monitoring
"""


@run.command()
def monitoring(**kwargs):
    """运行监控"""
    BeichiMonitor.run(**kwargs)


"""
下载外盘数据
pychanlun download-global-future-data
"""


@run.command()
def download_global_future_data(**kwargs):
    global_futures_downloader.run(**kwargs)


@run.command()
@click.option('--source', type=str, default="tdxlocal")
@click.option('--days', type=int, default=3)
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
def select_a_stock_signal(**kwargs):
    logging.info("股票信号计算 开始")
    a_stock_signal.run(**kwargs)
    logging.info("股票信号计算 结束")


@run.command()
@click.option('--code', type=str)
@click.option('--period', type=str)
def monitoring_a_stock_tdx(**kwargs):
    logging.info("股票监控 开始")
    stock_monitoring.run(**kwargs)
    logging.info("股票监控 结束")


if __name__ == '__main__':
    run()
