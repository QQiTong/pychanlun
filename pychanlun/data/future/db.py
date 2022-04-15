# -*- coding:utf-8 -*-

from QUANTAXIS.QAUtil.QADate import QA_util_datetime_to_strdatetime
from QUANTAXIS import QA_fetch_future_min_adv, QA_fetch_future_day_adv
from pychanlun.config import settings, cfg
from bson.codec_options import CodecOptions
from pychanlun.db import DBPyChanlun
import pymongo
import pandas as pd
from datetime import datetime, time
from pychanlun.database.cache import RedisCache


@RedisCache.memoize(expiration=900)
def fq_data_QA_fetch_future_min_adv(code, start, end=None, frequence='1min'):
    data = QA_fetch_future_min_adv(code, start, end, frequence)
    return data.data if data else None


@RedisCache.memoize(expiration=900)
def fq_data_QA_fetch_future_day_adv(code, start, end=None):
    data = QA_fetch_future_day_adv(code, start, end)
    return data.data if data else None


def fq_data_future_fetch_min(code, frequence, start=None, end=None, realtime=1):
    data = fq_data_QA_fetch_future_min_adv(code, QA_util_datetime_to_strdatetime(start), QA_util_datetime_to_strdatetime(end), frequence=frequence)
    if data is None:
        return None
    data.reset_index(inplace=True)
    data["time_stamp"] = data["datetime"].apply(lambda dt: cfg.TZ.localize(dt).timestamp())
    data.set_index("datetime", inplace=True, drop=False)
    if data is None or len(data) == 0:
        return None
    # 直接返回历史数据
    if realtime == 0:
        data['time'] = data['time_stamp']
        data = data.round({"open": 2, "high": 2, "low": 2, "close": 2, "position": 2, "volume": 2})
        return data
    last_datetime = data['datetime'][-1]
    last_datetime = cfg.TZ.localize(last_datetime)
    realtime_data_list = DBPyChanlun["future_realtime"].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=cfg.TZ)).find({
        "code": code, "type": frequence, "datetime": {"$gt": last_datetime}, "open": {"$gt": 0}, "high": {"$gt": 0}, "low": {"$gt": 0}, "close": {"$gt": 0}
    }).sort("datetime", pymongo.ASCENDING)
    realtime_data_list = pd.DataFrame(realtime_data_list)
    # print("实时数据",realtime_data_list,last_datetime)
    if 'volume' not in data.columns:
        data['volume'] = 0
    data = data[["code", "datetime", "open", "close", "high", "low", "position", 'volume', "time_stamp", "tradetime"]]
    if len(realtime_data_list) > 0:
        if 'volume' not in realtime_data_list.columns:
            realtime_data_list['volume'] = 0
        realtime_data_list['time_stamp'] = realtime_data_list['datetime'].apply(lambda value: value.timestamp())
        realtime_data_list['date_stamp'] = realtime_data_list['datetime'].apply(lambda value: value.replace(hour=0, minute=0, second=0).timestamp())
        realtime_data_list = realtime_data_list[["code", "datetime", "open", "close", "high", "low", "position", 'volume', "time_stamp", "tradetime"]]
        realtime_data_list['datetime'] = realtime_data_list['datetime'].apply(lambda value: value.replace(tzinfo=None))
        realtime_data_list.set_index('datetime', drop=False, inplace=True)
        data = data.append(realtime_data_list)
        data.drop_duplicates(subset="datetime", keep="first", inplace=True)
    data['time'] = data['time_stamp']
    data = data.round({"open": 2, "high": 2, "low": 2, "close": 2, "position": 2, "volume": 2})
    return data


def fq_data_future_fetch_day(code, start=None, end=None):
    data = fq_data_QA_fetch_future_day_adv(code, QA_util_datetime_to_strdatetime(start), QA_util_datetime_to_strdatetime(end))
    if data is None:
        return None
    data.reset_index(inplace=True)
    data['datetime'] = data['date'].apply(lambda x: datetime.combine(x, time()))
    data['date_stamp'] = data['datetime'].apply(lambda x: x.timestamp())
    data['time_stamp'] = data['date_stamp']
    data = data.round({"open": 2, "high": 2, "low": 2, "close": 2, "volume": 2, "amount": 2})
    data.set_index('datetime', drop=False, inplace=True)
    return data
