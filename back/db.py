import pymongo
import os
from .config import config

cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
settings = cfg.MONGODB_SETTINGS
MongoClient = pymongo.MongoClient(
    host = settings.get('host', '127.0.0.1'),
    port = settings.get('port', 27017),
    username = settings.get('username', ''),
    password = settings.get('password', ''),
    authSource = 'admin')
DBPyChanlun = MongoClient['pychanlun']
