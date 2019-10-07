import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
import os
import atexit
import pydash
from rqdatac import *
from .config import config
from .monitor import MarketData
from .monitor import CleanData
from .monitor import strategy3
from .monitor import strategy4
from .db import DBPyChanlun


def app():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='%(asctime)s %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

    init('license',
         'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
         ('rqdatad-pro.ricequant.com', 16011))

    scheduler = BlockingScheduler({
        'apscheduler.timezone': 'Asia/Shanghai'
    })
    atexit.register(lambda: scheduler.shutdown(wait=False))

    # 一个标的一个任务下载行情数据
    symbol_list = DBPyChanlun['symbol'].find()
    for symbol in symbol_list:
        s = {'code': symbol['code'], 'backend': symbol['backend']}
        scheduler.add_job(MarketData.getMarketData, 'interval', [s], seconds=15)
        scheduler.add_job(strategy3.doCaculate, 'interval', [s], seconds=60)
        scheduler.add_job(strategy4.doCaculate, 'interval', [s], seconds=60)
    scheduler.add_job(CleanData.doClean, 'interval', hours = 1)

    scheduler.start()


if __name__ == '__main__':
    app()
