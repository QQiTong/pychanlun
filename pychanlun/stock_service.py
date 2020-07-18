# -*- coding: utf-8 -*-

import pandas as pd
import pymongo
import pytz
from bson.codec_options import CodecOptions
from func_timeout import func_set_timeout

from pychanlun.db import DBPyChanlun

tz = pytz.timezone('Asia/Shanghai')


@func_set_timeout(60)
def get_stock_signal_list(page=1):
    data = DBPyChanlun["stock_signal"] \
        .with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=tz)) \
        .find({}) \
        .sort("fire_time", pymongo.DESCENDING).skip((page - 1) * 1000) \
        .limit(1000)
    df = pd.DataFrame(data)
    df = df.drop(columns=["_id"])
    df["fire_time"] = df["fire_time"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
    return df.to_dict("records")
