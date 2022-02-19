# -*- coding: utf-8 -*-

import pymongo
from pychanlun.config import settings
from pydash import get

host = get(settings, 'mongodb.host', '127.0.0.1')
port = get(settings, 'mongodb.port', 27017)
db = get(settings, 'mongodb.db', 'pychanlun')

MongoClient = pymongo.MongoClient(host=host, port=port, tz_aware=True)
DBPyChanlun = MongoClient[db]
DBQuantAxis = MongoClient['quantaxis']
