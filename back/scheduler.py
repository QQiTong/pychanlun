import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import sys

from back.monitor import strategy3

def app():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    scheduler = BlockingScheduler({
        'apscheduler.timezone': 'Asia/shanghai'
    })
    scheduler.add_job(strategy3.doMonitor1, 'cron', minute='*/3', hour="*")
    scheduler.add_job(strategy3.doMonitor2, 'cron', minute='*/15', hour="*")
    scheduler.start()

if __name__ == '__main__':
    app()
