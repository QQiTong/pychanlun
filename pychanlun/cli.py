# -*- coding: utf-8 -*-

from loguru import logger
import click
from pychanlun import server as api_server
from pychanlun.monitor import BeichiMonitor
from pychanlun.select import a_stock_signal
from pychanlun.market_data import tdx_local_downloader, global_futures_downloader
from pychanlun.monitor import a_stock_tdx as stock_monitoring
from pychanlun.job import save_all_job, save_xdxr_job, save_future_job
from pychanlun.zero.notify import send_ding_message


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
@click.option('--loop/--no-loop', default=True)
def monitoring(**kwargs):
    """运行监控"""
    BeichiMonitor.run(**kwargs)


# 下载外盘数据
# pychanlun download-global-future-data
@run.command()
@click.option('--loop/--no-loop', default=True)
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
        logger.info("从通达信下载股票数据 开始")
        tdx_local_downloader.run(**kwargs)
        logger.info("从通达信下载股票数据 完成")


@run.command()
@click.option('--code', type=str)
@click.option('--period', type=str)
def select_a_stock(**kwargs):
    logger.info("股票信号计算 开始")
    a_stock_signal.run(**kwargs)
    logger.info("股票信号计算 结束")


@run.command()
@click.option('--code', type=str)
@click.option('--period', type=str)
@click.option('--loop/--no-loop', default=True)
def monitoring_a_stock_tdx(**kwargs):
    logger.info("股票监控 开始")
    stock_monitoring.run(**kwargs)
    logger.info("股票监控 结束")


@run.command()
@click.option('--auto-shutdown/--no-auto-shutdown', default=False)
def save_all(**kwargs):
    save_all_job.run(**kwargs)
    send_ding_message("【事件通知】期货数据下载完成")

@run.command()
@click.option('--auto-shutdown/--no-auto-shutdown', default=False)
def save_future(**kwargs):
    save_future_job.run(**kwargs)
    send_ding_message("【事件通知】期货数据下载完成")

@run.command()
def save_xdxr(**kwargs):
    save_xdxr_job(**kwargs)
    send_ding_message("【事件通知】XDXR数据下载完成")


if __name__ == '__main__':
    run()
