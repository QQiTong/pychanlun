from flask import Flask
import os
import sys
from flask_apscheduler import APScheduler
import logging
from .config import config

from back.monitor import strategy3

if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(config[os.getenv('PYCHANLUN_CONFIG_ENV', default='default')])
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    logging.basicConfig(stream=sys.stdout,level = logging.INFO)

    app.apscheduler.add_job(func=strategy3.doMonitor1, id='strategy3.doMonitor1', trigger='cron', minute='*/3', hour="*")
    app.apscheduler.add_job(func=strategy3.doMonitor2, id='strategy3.doMonitor2', trigger='cron', minute='*/15', hour="*")

    app.run(host = '0.0.0.0')