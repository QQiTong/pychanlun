# -*- coding:utf-8 -*-

from pychanlun.config import settings
import redis
import pydash

host = pydash.get(settings, 'redis.host', '127.0.0.1')
port = pydash.get(settings, 'redis.port', 6379)
db = pydash.get(settings, 'redis.db', 1)
password = pydash.get(settings, 'redis.password')

RedisPool = redis.ConnectionPool(host=host, port=port, db=db, password=password, decode_responses=True)
RedisDB = redis.StrictRedis(connection_pool=RedisPool)
