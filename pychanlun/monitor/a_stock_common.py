# -*- coding: utf-8 -*-

import datetime

import pytz
from bson.codec_options import CodecOptions
from loguru import logger

from pychanlun.db import DBPyChanlun
from pychanlun.db import DBQuantAxis
from pychanlun.zerodegree.notify import send_ding_message

tz = pytz.timezone('Asia/Shanghai')


def save_a_stock_signal(sse, symbol, code, period, remark, fire_time, price, stop_lose_price, position, tags=[], category="", force_log=False):
    # 股票只是BUY_LONG才记录
    if position == "BUY_LONG":
        stock_one = DBQuantAxis['stock_list'].find_one({"code": code, "sse": sse})
        name = stock_one['name'] if stock_one is not None else None
        x = DBPyChanlun['stock_signal'] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find_one_and_update({
                "symbol": symbol,
                "code": code,
                "period": period,
                "fire_time": fire_time,
                "position": position
            }, {
                '$set': {
                    "symbol": symbol,
                    'code': code,
                    'name': name,
                    'period': period,
                    'remark': remark,
                    'fire_time': fire_time,
                    'price': price,
                    'stop_lose_price': stop_lose_price,
                    'position': position,
                    'tags': tags,
                    'category': category
                }
            }, upsert=True)
        if x is None and fire_time > datetime.datetime.now(tz=tz) - datetime.timedelta(days=30):
            # 首次信号，做通知
            content = "【事件通知】%s-%s-%s-%s-%s-%s-%s-%s" \
                      % (symbol, name, period, remark, fire_time.strftime("%m%d%H%M"), price, tags, category)
            if fire_time > datetime.datetime.now(tz=tz) - datetime.timedelta(hours=1):
                logger.info(content)
                send_ding_message(content)
            elif force_log:
                logger.info(content)
