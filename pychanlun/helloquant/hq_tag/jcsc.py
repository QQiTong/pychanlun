# -*- encoding: utf-8 -*-

import numpy as np
import QUANTAXIS as QA
import pandas as pd

"""
金叉死叉标记，返回的格式：
{
    "buy_ma_gold_cross": {
        "idx": [5],
        "date": ["2020-11-22 10:15"],
        "data": [2003],
        "stop_lose_price": [1998]
    },
    "sell_ma_dead_cross": {
        "idx": [20],
        "date": ["2020-11-22 10:15"],
        "data": [2003],
        "stop_lose_price": [2100]
    }
}
"""


def find_jcsc_tags(time_str_array: np.array, high_array: np.array, low_array: np.array, close_array: np.array, fast_window: int = 5, slow_window: int = 34):
    r = {
        "buy_ma_gold_cross": {
            "idx": [],
            "date": [],
            "data": [],
            "stop_lose_price": [],
            "stop_win_price":[]
        },
        "sell_ma_dead_cross": {
            "idx": [],
            "date": [],
            "data": [],
            "stop_lose_price": [],
            "stop_win_price":[]
        }
    }
    fast_ma = QA.MA(pd.Series(close_array), fast_window)
    slow_ma = QA.MA(pd.Series(close_array), slow_window)
    jc = QA.CROSS(fast_ma, slow_ma).fillna(0)
    sc = QA.CROSS(slow_ma, fast_ma).fillna(0)
    for idx in range(len(jc)):
        if jc[idx] == 1:
            r["buy_ma_gold_cross"]["idx"].append(idx)
            r["buy_ma_gold_cross"]["date"].append(time_str_array[idx])
            r["buy_ma_gold_cross"]["data"].append(close_array[idx])
            r["buy_ma_gold_cross"]["stop_lose_price"].append(low_array[idx-1] if idx > 0 else low_array[idx])
    for idx in range(len(sc)):
        if sc[idx] == 1:
            r["sell_ma_dead_cross"]["idx"].append(idx)
            r["sell_ma_dead_cross"]["date"].append(time_str_array[idx])
            r["sell_ma_dead_cross"]["data"].append(close_array[idx])
            r["sell_ma_dead_cross"]["stop_lose_price"].append(high_array[idx-1] if idx > 0 else high_array[idx])
    return r
