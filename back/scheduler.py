import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
import os
import atexit

from rqdatac import *
from mongoengine import connect
from .config import config

from .monitor import MarketData
from .monitor import CleanData
from back.monitor import strategy3


def app():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='%(asctime)s %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

    cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
    mongodbSettings = cfg.MONGODB_SETTINGS
    connect('pychanlun', host=mongodbSettings.get('host', '127.0.0.1'), port=mongodbSettings.get('port', 27017),
            username=mongodbSettings.get('username', ''), password=mongodbSettings.get('password', ''), authentication_source='admin')

    init('license',
         'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
         ('rqdatad-pro.ricequant.com', 16011))

    scheduler = BlockingScheduler({
        'apscheduler.timezone': 'Asia/Shanghai'
    })
    atexit.register(lambda: scheduler.shutdown(wait=False))

    scheduler.add_job(MarketData.getMarketData1, 'cron', minute='*/1', hour='*')
    scheduler.add_job(MarketData.getMarketData2, 'cron', minute='*/5', hour='*')
    scheduler.add_job(strategy3.doMonitor, 'cron', minute='*/1', hour="*")
    scheduler.add_job(CleanData.doClean, 'interval', hours = 1)

    scheduler.start()


if __name__ == '__main__':
    app()
