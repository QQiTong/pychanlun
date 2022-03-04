# -*- coding:utf-8 -*-

from pychanlun.database.cache import RedisCache
from pychanlun.db import DBPyChanlun
from bson.codec_options import CodecOptions
import pydash
from pychanlun.config import cfg
import pymongo
import pandas as pd
from pychanlun.util.code import fq_util_code_append_market_code


@RedisCache.memoize()
def get_stock_holding_codes():
    records = list(DBPyChanlun["stock_fills"].with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=cfg.TZ)).find({
            "op": "买",
            "settle": {
                "$ne": 1
            }
        }))
    codes = pydash.chain(records).map(
        lambda record: record.get("symbol")).uniq().value()
    return codes


def get_stock_last_fill(symbol):
    records = list(DBPyChanlun["stock_fills"].with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=cfg.TZ)).find({
            "symbol":
            symbol,
            "op":
            "买",
            "settle": {
                "$ne": 1
            }
        }).sort([("date", pymongo.DESCENDING), ("time", pymongo.DESCENDING)]))
    if len(records) > 0:
        return records[0]
    else:
        return None


def get_stock_fills(symbol):
    records = DBPyChanlun["stock_fills"].with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=cfg.TZ)).find({
            "symbol":
            symbol,
            "op":
            "买",
            "settle": {
                "$ne": 1
            }
        }).sort([("date", pymongo.DESCENDING), ("time", pymongo.DESCENDING)])
    df = pd.DataFrame(records)
    if not df.empty:
        if "settle_quantity" not in df.columns:
            df["settle_quantity"] = 0
        else:
            df["settle_quantity"] = df["settle_quantity"].fillna(0)
    return df


def get_stock_positions():
    records = DBPyChanlun["stock_fills"].with_options(
        codec_options=CodecOptions(tz_aware=True, tzinfo=cfg.TZ)).find({}).sort([("date", pymongo.DESCENDING), ("time", pymongo.DESCENDING)])
    df = pd.DataFrame(records)
    df.drop(columns=["_id"], inplace=True)
    df["symbol"] = df["symbol"].apply(lambda x: fq_util_code_append_market_code(x))
    if "settle_quantity" not in df.columns:
        df["settle_quantity"] = 0
    df["settle_quantity"] = df["settle_quantity"].fillna(0)
    df["direction"] = df["op"].apply(lambda op:  -1 if op == '买' else 1)
    df["amount"] = df["amount"] * df["direction"]
    df["commission"] = df["commission"] * -1
    df["tax"] = df["tax"] * -1
    df["quantity"] = df["quantity"] * df["direction"] * -1
    df = df.groupby(by=["symbol"]).agg({"symbol": "first", "name": "first", "quantity": "sum", "amount": "sum", "commission": "sum", "tax": "sum", "date":"last", "time": "last"})
    df = df[df['amount']<0]
    df = df.sort_values(by=["date", "time"])
    return df.to_dict(orient="records")
