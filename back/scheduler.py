from apscheduler.schedulers.blocking import BlockingScheduler
import logging

from back.monitor import strategy3

if __name__ == '__main__':
    print('启动监控任务')
    scheduler = BlockingScheduler({
        'apscheduler.timezone': 'Asia/shanghai'
    })
    scheduler.add_job(strategy3.doMonitor1, 'cron', minute='*/3', hour="*")
    scheduler.add_job(strategy3.doMonitor2, 'cron', minute='*/15', hour="*")
    scheduler.start()
