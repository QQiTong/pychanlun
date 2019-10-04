import pymongo
import os
from .config import config

cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
settings = cfg.MONGODB_SETTINGS
MongoClient = pymongo.MongoClient(settings.get('url', ''))
DBPyChanlun = MongoClient['pychanlun']
