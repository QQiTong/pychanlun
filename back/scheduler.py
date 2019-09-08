import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
import os
from mongoengine import connect
from .config import config

from .monitor import MarketData
from back.monitor import strategy3


def app():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

    cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
    mongodbSettings = cfg.MONGODB_SETTINGS
    connect('pychanlun', host=mongodbSettings['host'], port=mongodbSettings['port'],
            username=mongodbSettings['username'], password=mongodbSettings['password'], authentication_source='admin')

    scheduler = BlockingScheduler({
        'apscheduler.timezone': 'Asia/shanghai'
    })
    scheduler.add_job(MarketData.getMarketData1, 'cron', minute='*/3', hour='*')
    scheduler.add_job(strategy3.doMonitor1, 'cron', minute='*/3', hour="*")
    scheduler.add_job(strategy3.doMonitor2, 'cron', minute='*/15', hour="*")
    scheduler.start()


if __name__ == '__main__':
    app()
