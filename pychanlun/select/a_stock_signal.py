# -*- coding: utf-8 -*-

import decimal
import logging
import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytz
from bson.codec_options import CodecOptions

from pychanlun.chanlun_service import get_data
from pychanlun.db import DBPyChanlun
from pychanlun.db import DBQuantAxis
from pychanlun.monitor.a_stock_common import save_a_stock_signal
import QUANTAXIS as QA

tz = pytz.timezone('Asia/Shanghai')


def run(**kwargs):
    # 清理掉1年以上的数据
    cutoff_time = datetime.now(tz) - timedelta(days=360)
    DBPyChanlun["stock_signal"] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .delete_many({"fire_time": {"$lte": cutoff_time}})

    periods = ['30m', '60m']
    symbol = kwargs.get('symbol')
    period = kwargs.get('period')
    code_period_list = []
    code_list = []
    if symbol is None:
        stock_list = DBQuantAxis["stock_list"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find()
        stock_list = pre_filter(stock_list)
        for stock in stock_list:
            symbol = "%s%s" % (stock["sse"], stock["code"])
            code_list.append({"sse": stock["sse"], "symbol": symbol, "code": stock["code"]})
            if period is None:
                for period in periods:
                    code_period_list.append(
                        {"sse": stock["sse"], "symbol": symbol, "code": stock["code"], "period": period})
            else:
                code_period_list.append(
                    {"sse": stock["sse"], "symbol": symbol, "code": stock["code"], "period": period})
    else:
        sse = symbol[:2]
        code = symbol[2:]
        if period is None:
            for period in periods:
                code_period_list.append({'sse': sse, 'symbol': symbol, 'code': code, 'period': period})
        else:
            code_period_list.append({'sse': sse, 'symbol': symbol, 'code': code, 'period': period})

    for idx in range(len(code_list)):
        calculate_raising_limit(code_list[idx])
    for idx in range(len(code_period_list)):
        calculate_chanlun_signal(code_period_list[idx])

    export_to_tdx()


def pre_filter(stock_list):
    cutoff_time = datetime.now(tz) - timedelta(days=100)
    result = []
    for stock in stock_list:
        bars = DBQuantAxis["stock_day"] \
            .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
            .find({"code": stock["code"], "date_stamp": {"$gte": cutoff_time.timestamp()}})
        bars = pd.DataFrame(bars)
        if len(bars) > 0:
            ma34 = QA.MA(bars.close, 34)
            if 2 < ma34.iloc[-1] < bars.close.iloc[-1] < 20:
                result.append(stock)
            continue
        DBPyChanlun["stock_signal"].delete_many({"sse": stock["sse"], "code": stock["code"]})
    return result


def calculate_raising_limit(code_obj):
    sse = code_obj["sse"]
    symbol = code_obj["symbol"]
    code = code_obj["code"]
    cutoff_time = datetime.now(tz) - timedelta(days=11)
    bars = DBQuantAxis["stock_day"] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .find({"code": code, "date_stamp": {"$gte": cutoff_time.timestamp()}})
    bars = pd.DataFrame(bars)
    if len(bars) < 3:
        return
    cur_close = bars['close'].apply(lambda x: decimal.Decimal('%.2f' % x))
    pre_close = bars['close'].shift(periods=1).apply(lambda x: decimal.Decimal('%.2f' % x))
    cur_close = cur_close[1:]
    pre_close = pre_close[1:]
    bars = bars[1:]
    bars['limit_up'] = cur_close >= (pre_close * decimal.Decimal('1.1')).apply(
        lambda x: x.quantize(decimal.Decimal('0.00')))
    for idx in bars.index:
        if bars.loc[idx, 'limit_up']:
            save_a_stock_signal(
                sse,
                symbol,
                code,
                '180m',
                '涨停',
                datetime.fromtimestamp(bars.loc[idx, 'date_stamp'], timezone.utc),
                bars.loc[idx, 'close'],
                bars.loc[idx, 'open'],
                'BUY_LONG',
                ['涨停'],
                "涨停",
                True
            )


def calculate_chanlun_signal(code_period_obj):
    sse = code_period_obj["sse"]
    symbol = code_period_obj["symbol"]
    code = code_period_obj["code"]
    period = code_period_obj["period"]
    resp = get_data(symbol, period, datetime.now().strftime("%Y-%m-%d"))
    signal_map = {
        "buy_zs_huila": "回拉中枢看涨",
        "buy_zs_tupo": "突破中枢看涨",
        "buy_v_reverse": "V反看涨",
        "buy_five_v_reverse": "五浪V反看涨",
        "buy_duan_break": "线段破坏看涨"
    }
    for signal in signal_map:
        signals = resp[signal]
        for idx in range(len(signals["date"])):
            fire_time = signals["date"][idx]
            fire_time = tz.localize(datetime.strptime(fire_time, "%Y-%m-%d %H:%M"))
            price = signals["data"][idx]
            stop_lose_price = signals["stop_lose_price"][idx]
            tag = signals["tag"][idx]
            tags = [] if tag is None else tag.split(",")
            save_a_stock_signal(
                sse,
                symbol,
                code,
                period,
                signal_map[signal],
                fire_time,
                price,
                stop_lose_price,
                'BUY_LONG',
                tags,
                "",
                True
            )


def export_to_tdx():
    TDX_HOME = os.environ.get("TDX_HOME")
    if TDX_HOME is None:
        logging.error("没有指定通达信安装目录环境遍历（TDX_HOME）")
        return
    t = datetime.now(tz) - timedelta(days=30)
    t = t.replace(hour=0, minute=0, second=0, microsecond=0)
    signals = DBPyChanlun['stock_signal'] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .find({'period': {'$in': ['30m', '60m', '180m']}, 'fire_time': {'$gte': t}})
    signals = pd.DataFrame(signals).drop_duplicates(["symbol"])
    signals["group"] = signals["fire_time"].apply(lambda v: v.strftime("%d"))

    for x in range(1, 32):
        group = str(x).zfill(2)
        result = signals[signals["group"] == group]
        seq = []
        for _, row in result.iterrows():
            symbol = row["symbol"]
            if symbol.startswith("sh"):
                symbol = symbol.replace("sh", "1")
            elif symbol.startswith("sz"):
                symbol = symbol.replace("sz", "0")
            else:
                continue
            seq.append(symbol + "\n")
        with open(os.path.join(TDX_HOME, "T0002\\blocknew\\CL%s.blk" % group), "w") as fo:
            fo.writelines(seq)
