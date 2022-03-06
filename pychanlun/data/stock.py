# -*- coding: utf-8 -*-

import pymongo
import os
import pandas as pd

from pydash import get
from datetime import datetime, time
from bson.codec_options import CodecOptions
from pychanlun.db import DBPyChanlun
from pychanlun.util.code import fq_util_code_append_market_code
from pychanlun.config import settings, cfg
from QUANTAXIS.QAUtil.QADate import QA_util_datetime_to_strdatetime
from QUANTAXIS import QA_fetch_stock_min_adv, QA_fetch_stock_day_adv


def fq_data_stock_fetch_min(code, frequence, start=None, end=None, useCustomData=False):
    data = None
    if frequence in ['5min', '30min', '60min', '90min', '120min']:
        if useCustomData:
            data_tdx = pd.read_csv(
                os.path.join(get(settings, "custom.data.dir"), "data_tdx.csv"))
            for _, row in data_tdx.iterrows():
                if row["code"][3:] == code:
                    data = pd.read_csv(os.path.join(get(settings, "custom.data.dir"), "data_stand_format_%s" % frequence, "%s.csv" % row["code"]))
                    if len(data) > 3000:
                        data = data[-3000:]
                    data["datetime"] = data["time"].apply(
                        lambda x: datetime.strptime(x, "%Y-%m-%d %H%M"))
                    data["time_stamp"] = data["datetime"].apply(lambda dt: cfg.TZ.localize(dt).timestamp())
                    data["date_stamp"] = data["datetime"].apply(
                        lambda dt: cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
                    data["volume"] = data["vol"]
                    data["amount"] = data["volume"]
                    data.set_index("datetime", drop=False, inplace=True)
                    break
    if data is None:
        data = QA_fetch_stock_min_adv(code, QA_util_datetime_to_strdatetime(start), QA_util_datetime_to_strdatetime(end), frequence=frequence).to_qfq().data
        data.reset_index(inplace=True)
        data["time_stamp"] = data["datetime"].apply(lambda dt: cfg.TZ.localize(dt).timestamp())
        data.set_index("datetime", inplace=True, drop=False)
    if data is None or len(data) == 0:
        return None
    last_datetime = data['datetime'][-1]
    # TODO: 取实时数据部分优化
    realtime_data_list = DBPyChanlun["stock_realtime"].with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=cfg.TZ)).find({"code": fq_util_code_append_market_code(code, upper_case=False),
            "frequence": frequence, "datetime": {"$gt": last_datetime, "$lte": end},
            "open": {"$gt": 0}, "high": {"$gt": 0}, "low": {"$gt": 0}, "close": {"$gt": 0}
        }).sort("datetime", pymongo.ASCENDING)
    realtime_data_list = pd.DataFrame(realtime_data_list)
    data = data[["datetime", "open", "close", "high", "low", "volume", "amount", "time_stamp"]]
    if len(realtime_data_list) > 0:
        realtime_data_list['time_stamp'] = realtime_data_list['datetime'].apply(lambda value: value.timestamp())
        realtime_data_list['date_stamp'] = realtime_data_list['datetime'].apply(lambda value: value.replace(hour=0, minute=0, second=0).timestamp())
        realtime_data_list = realtime_data_list[["datetime", "open", "close", "high", "low", "volume", "amount", "time_stamp"]]
        realtime_data_list['datetime'] = realtime_data_list['datetime'].apply(lambda value: value.replace(tzinfo=None))
        realtime_data_list.set_index('datetime', drop=False, inplace=True)
        data = data.append(realtime_data_list)
        data.drop_duplicates(subset="datetime", keep="first", inplace=True)
    data = data.round({"open": 2, "high": 2, "low": 2, "close": 2, "volume": 2, "amount": 2})
    return data


def fq_data_stock_fetch_day(code, start=None, end=None, useCustomData=False):
    data = None
    if useCustomData:
        data_tdx = pd.read_csv(
            os.path.join(get(settings, "custom.data.dir"), "data_tdx.csv"))
        for _, row in data_tdx.iterrows():
            if row["code"][3:] == code:
                data = pd.read_csv(
                    os.path.join(get(settings, "custom.data.dir"),
                                 "data_stand_format_1d",
                                 "%s.csv" % row["code"]))
                if len(data) > 3000:
                    data = data[-3000:]
                data["datetime"] = data["time"].apply(
                    lambda x: cfg.TZ.localize(datetime.strptime(x, "%Y-%m-%d")
                                              ))
                data["time_stamp"] = data["datetime"].apply(
                    lambda dt: dt.timestamp())
                data["date_stamp"] = data["datetime"].apply(
                    lambda dt: cfg.TZ.localize(
                        datetime(year=dt.year, month=dt.month, day=dt.day)
                    ).timestamp())
                data["volume"] = data["vol"]
                data["amount"] = data["volume"]
                data.set_index("datetime", drop=False, inplace=True)
                break
    if data is None:
        data = QA_fetch_stock_day_adv(
            code, QA_util_datetime_to_strdatetime(start),
            QA_util_datetime_to_strdatetime(end)).to_qfq().data
        data.reset_index(inplace=True)
        data['datetime'] = data['date'].apply(
            lambda x: datetime.combine(x, time()))
        data['date_stamp'] = data['datetime'].apply(lambda x: x.timestamp())
        data['time_stamp'] = data['date_stamp']
        data = data.round({"open": 2, "high": 2, "low": 2, "close": 2, "volume": 2, "amount": 2})
        data.set_index('datetime', drop=False, inplace=True)
    return data


def fq_data_stock_resample_60min(data):
    def func(dt):
        if dt.time() > time(hour=9, minute=30) and dt.time() <= time(hour=10, minute=30):
            return cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day, hour=10, minute=30))
        elif dt.time() > time(hour=10, minute=30) and dt.time() <= time(hour=11, minute=30):
            return cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day, hour=11, minute=30))
        elif dt.time() > time(hour=13, minute=0) and dt.time() <= time(hour=14, minute=0):
            return cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day, hour=14, minute=0))
        elif dt.time() > time(hour=14, minute=0) and dt.time() <= time(hour=15, minute=0):
            return cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day, hour=15, minute=0))

    data["group"] = data["datetime"].apply(func)
    data = data.groupby(by="group").agg({
        "datetime": "last",
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "amount": "sum"
    })
    data["time_stamp"] = data["datetime"].apply(lambda dt: dt.timestamp())
    data["date_stamp"] = data["datetime"].apply(lambda dt: cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
    data = data.round({"open": 2, "high": 2, "low": 2, "close": 2, "volume": 2, "amount": 2})
    data.set_index("datetime", drop=True, inplace=True)
    return data


def fq_data_stock_resample_90min(data):
    def func(dt):
        if dt.time() > time(hour=9, minute=30) and dt.time() <= time(hour=11, minute=0):
            return cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day, hour=10, minute=30))
        elif dt.time() > time(hour=11, minute=0) and dt.time() <= time(hour=14, minute=0):
            return cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day, hour=11, minute=30))
        elif dt.time() > time(hour=14, minute=0) and dt.time() <= time(hour=15, minute=0):
            return cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day, hour=14, minute=0))

    data["group"] = data["datetime"].apply(func)
    data = data.groupby(by="group").agg({
        "datetime": "last",
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "amount": "sum"
    })
    data["time_stamp"] = data["datetime"].apply(lambda dt: dt.timestamp())
    data["date_stamp"] = data["datetime"].apply(lambda dt: cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
    data = data.round({"open": 2, "high": 2, "low": 2, "close": 2, "volume": 2, "amount": 2})
    data.set_index("datetime", drop=True, inplace=True)
    return data


def fq_data_stock_resample_120min(data):
    def func(dt):
        if dt.time() > time(hour=9, minute=30) and dt.time() <= time(hour=11, minute=30):
            return cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day, hour=10, minute=30))
        elif dt.time() > time(hour=13, minute=0) and dt.time() <= time(hour=15, minute=0):
            return cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day, hour=11, minute=30))

    data["group"] = data["datetime"].apply(func)
    data = data.groupby(by="group").agg({
        "datetime": "last",
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        "amount": "sum"
    })
    data["time_stamp"] = data["datetime"].apply(lambda dt: dt.timestamp())
    data["date_stamp"] = data["datetime"].apply(lambda dt: cfg.TZ.localize(
        datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
    data = data.round({"open": 2, "high": 2, "low": 2, "close": 2, "volume": 2, "amount": 2})
    data.set_index("datetime", drop=True, inplace=True)
    return data
