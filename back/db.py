import pymongo
import os
from back.config import cfg

settings = cfg.MONGODB_SETTINGS
MongoClient = pymongo.MongoClient(settings.get('url', ''), tz_aware=True)
DBPyChanlun = MongoClient['pychanlun']
