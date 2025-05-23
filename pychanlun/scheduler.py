# -*- coding: utf-8 -*-

import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import logging
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.blocking import BlockingScheduler
import atexit
import pydash
import pytz
from rqdatac import *
from apscheduler.executors.pool import ThreadPoolExecutor

from pychanlun.config import config
from pychanlun.monitor import MarketData
from pychanlun.monitor import CleanData
from pychanlun.monitor import strategy3
from pychanlun.monitor import strategy4
from pychanlun.db import DBPyChanlun

tz = pytz.timezone('Asia/Shanghai')

def app():
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(threadName)s %(levelname)s %(message)s')
    logger = logging.getLogger()
    logfile = os.path.join(BASE_DIR, "logs\pychanlun-scheduler.log")
    handler = RotatingFileHandler(filename=logfile, maxBytes=10*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    init('license',
         'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
         ('rqdatad-pro.ricequant.com', 16011))

    symbol_list = list(DBPyChanlun['symbol'].find({"monitoring": True}))
    size = len(symbol_list)
    executors = {
        'default': ThreadPoolExecutor(size*5),
    }
    scheduler = BlockingScheduler(executors=executors, timezone=tz)
    atexit.register(lambda: scheduler.shutdown(wait=False))

    for symbol in symbol_list:
        s = {'code': symbol['code'], 'backend': symbol['backend']}
        scheduler.add_job(MarketData.getMarketData, 'interval', [s], seconds=15)
        scheduler.add_job(strategy3.doCaculate, 'interval', [s], seconds=30)
        scheduler.add_job(strategy4.doCaculate, 'interval', [s], seconds=30)
    scheduler.add_job(CleanData.doClean, 'interval', hours = 1)

    scheduler.start()


if __name__ == '__main__':
    app()
