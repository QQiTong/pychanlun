# -*- coding: utf-8 -*-

import pymongo
import os
from pychanlun.config import cfg

settings = cfg.MONGODB_SETTINGS
MongoClient = pymongo.MongoClient(settings.get('url', ''), tz_aware=True)
DBPyChanlun = MongoClient['pychanlun']
DBQuantAxis = MongoClient['quantaxis']