# -*- coding: utf-8 -*-

import datetime

import pytz
from bson.codec_options import CodecOptions
from loguru import logger

from pychanlun.db import DBPyChanlun
from pychanlun.db import DBQuantAxis
from pychanlun.zero.notify import send_ding_message

tz = pytz.timezone('Asia/Shanghai')


def save_a_stock_signal(sse, symbol, code, period, remark, fire_time, price, stop_lose_price, position, tags=[], category=""):
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
        if x is None and fire_time >= datetime.datetime.now(tz=tz).replace(hour=0, minute=0, second=0, microsecond=0):
            # 首次信号，做通知
            content = "【事件通知】 %s,%s,%s,%s,时间%s,价格%s,止损率%.2f" \
                      % (symbol, name, period, remark, fire_time.strftime("%m%dT%H:%M"), price, (stop_lose_price - price) / price * 100)
            if category is not None and len(category.strip()) > 0:
                content = content + "," + category
            if tags is not None and len(",".join(tags).strip()) > 0:
                content = content + "," + ",".join(tags).strip()
            logger.info(content)
            send_ding_message(content)
