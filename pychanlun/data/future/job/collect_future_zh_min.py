# -*- coding: utf-8 -*-

import signal
import threading
import traceback
from datetime import datetime, timedelta
from time import sleep

import durationpy
import jqdatasdk as jq
import pandas as pd
import pydash
import pymongo
from loguru import logger
from pymongo import UpdateOne

from pychanlun.config import cfg, settings, config
from QUANTAXIS.QAUtil import QA_util_if_tradetime, QA_util_if_trade
from pychanlun.database.redis import RedisDB
from pychanlun.db import DBPyChanlun
from pychanlun.data.future.tdx import fq_future_fetch_instrument_bars


SYMBOL_QUEUE_NAME = "future_zh_min_symbol_queue"
_is_test = pydash.get(settings, "test", False)
_running = True
future_list = []


def signal_handler(signalnum, frame):
    logger.info("正在停止程序。", signalnum, frame)
    global _running
    _running = False


def save_records(records):
    batch = pydash.chain(records).map(lambda record: UpdateOne(
        {"datetime": record["datetime"], "code": record["code"], "type": record["type"]},
        {"$set": record}, upsert=True)).value()
    DBPyChanlun["future_realtime"].bulk_write(batch)


def _save(df):
    source = df["source"][0]
    code = df["code"][0]
    df['time_stamp'] = df.index.to_series().apply(lambda v: v.timestamp())
    df["date_stamp"] = df.index.to_series().apply(lambda dt: cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
    df['tradetime'] = df.index.to_series().apply(lambda record: record if record.hour < 20 else record + timedelta(days=1))
    save_records(df.reset_index().to_dict(orient="records"))

    df = df.resample('5T', closed='right', label='right').agg(cfg.FUTURE_OHLC).dropna(how='any')
    df["code"] = code
    df["type"] = "5min"
    df["source"] = source
    df['time_stamp'] = df.index.to_series().apply(lambda v: v.timestamp())
    df["date_stamp"] = df.index.to_series().apply(lambda dt: cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
    df['tradetime'] = df.index.to_series().apply(lambda record: record if record.hour < 20 else record + timedelta(days=1))
    if len(df) > 1:
        save_records(df[1:].reset_index().to_dict(orient="records"))

    df = df.resample('15T', closed='right', label='right').agg(cfg.FUTURE_OHLC).dropna(how='any')
    df["code"] = code
    df["type"] = "15min"
    df["source"] = source
    df['time_stamp'] = df.index.to_series().apply(lambda v: v.timestamp())
    df["date_stamp"] = df.index.to_series().apply(lambda dt: cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
    df['tradetime'] = df.index.to_series().apply(lambda record: record if record.hour < 20 else record + timedelta(days=1))
    if len(df) > 1:
        save_records(df[1:].reset_index().to_dict(orient="records"))

    df = df.resample('30T', closed='right', label='right').agg(cfg.FUTURE_OHLC).dropna(how='any')
    df["code"] = code
    df["type"] = "30min"
    df["source"] = source
    df['time_stamp'] = df.index.to_series().apply(lambda v: v.timestamp())
    df["date_stamp"] = df.index.to_series().apply(lambda dt: cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
    df['tradetime'] = df.index.to_series().apply(lambda record: record if record.hour < 20 else record + timedelta(days=1))
    if len(df) > 1:
        save_records(df[1:].reset_index().to_dict(orient="records"))

    df = df.resample('60T', closed='right', label='right').agg(cfg.FUTURE_OHLC).dropna(how='any')
    df["code"] = code
    df["type"] = "60min"
    df["source"] = source
    df['time_stamp'] = df.index.to_series().apply(lambda v: v.timestamp())
    df["date_stamp"] = df.index.to_series().apply(lambda dt: cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
    df['tradetime'] = df.index.to_series().apply(lambda record: record if record.hour < 20 else record + timedelta(days=1))
    if len(df) > 1:
        save_records(df[1:].reset_index().to_dict(orient="records"))

    df = df.resample('1D', closed='right', label='left').agg(cfg.FUTURE_OHLC).dropna(how='any')
    df["code"] = code
    df["type"] = "1d"
    df["source"] = source
    df['time_stamp'] = df.index.to_series().apply(lambda v: v.timestamp())
    df["date_stamp"] = df.index.to_series().apply(lambda dt: cfg.TZ.localize(datetime(year=dt.year, month=dt.month, day=dt.day)).timestamp())
    df['tradetime'] = df.index.to_series().apply(lambda record: record if record.hour < 20 else record + timedelta(days=1))
    if len(df) > 1:
        save_records(df[1:].reset_index().to_dict(orient="records"))


def future_zh_min_tdx():
    global _running
    while _running:
        symbol = None
        try:
            # if not _is_test and RedisDB.llen(SYMBOL_QUEUE_NAME) == 0:
            #     seconds = tool_trade_date_seconds_to_start()
            #     if seconds > 0:
            #         seconds = min(seconds, 900)
            #         logger.info("%s from now on, %s sleep %s to resume" % (datetime.now().strftime(cfg.DT_FORMAT_FULL), "收集通达信分钟数据", durationpy.to_str(timedelta(seconds=seconds))))
            #         sleep(seconds)
            #         if tool_trade_date_seconds_to_start() > 0:
            #             continue
            symbol = RedisDB.brpop(SYMBOL_QUEUE_NAME)
            if symbol is None:
                continue
            symbol = symbol[1]
            df = fq_future_fetch_instrument_bars(symbol)
            if df is None or len(df) <= 0:
                RedisDB.lpush(SYMBOL_QUEUE_NAME, symbol)
                continue
            df = df[['open', 'high', 'low', 'close', 'position', 'trade', 'price', 'datetime', 'amount']]
            df['datetime'] = df['datetime'].apply(lambda record: cfg.TZ.localize(datetime.strptime(record, cfg.DT_FORMAT_M)))
            df['datetime'] = df['datetime'].apply(lambda record: record if record.hour < 20 else record - timedelta(days=1))
            df.set_index('datetime', inplace=True, drop=True)
            df['open'] = df['open'].astype('float64')
            df['close'] = df['close'].astype('float64')
            df['high'] = df['high'].astype('float64')
            df['low'] = df['low'].astype('float64')
            df["code"] = symbol
            df["type"] = "1min"
            df["source"] = "通达信"
            logger.info("%s 通达信" % symbol)
            _save(df)
        except Exception:
            logger.info("Error Occurred: {0}".format(traceback.format_exc()))
        sleep(1)


def future_zh_min_symbol_queue():
    global _running
    global future_list
    while _running:
        try:
            queue_length = RedisDB.llen(SYMBOL_QUEUE_NAME)
            # if not _is_test and queue_length == 0:
                # seconds = tool_trade_date_seconds_to_start()
                # if seconds > 0:
                #     seconds = min(seconds, 900)
                #     logger.info("%s from now on, %s sleep %s to resume" % (datetime.now().strftime(cfg.DT_FORMAT_FULL), "股票队列派发", durationpy.to_str(timedelta(seconds=seconds))))
                #     sleep(seconds)
                #     if tool_trade_date_seconds_to_start() > 0:
                #         continue
            if queue_length == 0:
                if len(future_list) > 0:
                    RedisDB.lpush(SYMBOL_QUEUE_NAME, *future_list)
        except Exception:
            logger.info("Error Occurred: {0}".format(traceback.format_exc()))
        sleep(1)


def job():
    global future_list
    for symbol in config['future_config']:
        # 到美原油为止
        if symbol == 'CL':
            break
        future_list.append(symbol + "L9")
    print("采集的品种列表", future_list)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    indexes = DBPyChanlun["future_realtime"].index_information()
    if "code_datetime_type" not in indexes:
        DBPyChanlun["future_realtime"].create_index(
            [
                ('code', pymongo.ASCENDING),
                ('datetime', pymongo.ASCENDING),
                ('type', pymongo.ASCENDING),
            ],
            unique=True,
            name="code_datetime_type")
    DBPyChanlun["future_realtime"].delete_many({
        "datetime": {
            "%lt": datetime.now() - timedelta(days=5)
        }
    })
    threading.Thread(target=future_zh_min_tdx, daemon=False).start()
    threading.Thread(target=future_zh_min_symbol_queue, daemon=False).start()


def main():
    job()


if __name__ == "__main__":
    main()
