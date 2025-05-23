# -*- coding:utf-8 -*-

from pychanlun.config import settings
from memoizit import Memoizer
import pydash

host = pydash.get(settings, 'redis.host', '127.0.0.1')
port = pydash.get(settings, 'redis.port', 6379)
db = pydash.get(settings, 'redis.db', 1)
password = pydash.get(settings, 'redis.password')

RedisCache = Memoizer(backend="redis", host=host, port=port, db=db)

InMemoryCache = Memoizer()
