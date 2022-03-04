# -*- coding:utf-8 -*-

from pydash import get
from pychanlun.database.cache import RedisCache
from pychanlun.db import DBQuantAxis

@RedisCache.memoize(expiration=864000)
def fq_fetch_a_stock_basic(code):
    return DBQuantAxis["stock_list"].find_one({"code": code})

@RedisCache.memoize(expiration=864000)
def fq_fetch_a_stock_category(code):
    stock_one = DBQuantAxis["stock_list"].find_one({"code": code})
    return get(stock_one, 'category', [])
