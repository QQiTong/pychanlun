from datetime import datetime, timedelta
import logging
from ..db import DBPyChanlun

# 清理久远的数据，数据库不要变的太大，行情数据保留360天
def doClean():
    logger = logging.getLogger()
    t = datetime.now() - timedelta(days = 360)
    collection_names = DBPyChanlun.list_collection_names()
    for collection_name in collection_names:
        DBPyChanlun[collection_name].delete_many({
            'date_created': { '$lte': t }
        })
    # 策略日志数据保留1个月
    t = datetime.now() - timedelta(days = 30)
    for i in range(1, 5):
        collection_name = 'stragegy%s_log' % i
        logger.info('%s clean' % collection_name)
        if collection_name in collection_names:
            DBPyChanlun[collection_name].delete_many({
                'date_created': { '$lte': t }
            })
