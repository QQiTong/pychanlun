# -*- coding:utf-8 -*-

import queue
import datetime
import uvicorn
from pytdx.exhq import TdxExHq_API
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Timer
from QUANTAXIS.QAUtil.QASetting import future_ip_list
from fastapi import FastAPI
from pychanlun.basic.singleton_type import SingletonType

class TdxExHqExecutor(metaclass=SingletonType):
    def __init__(self, thread_num=5, timeout=1, sleep_time=1, *args, **kwargs):
        self.thread_num = thread_num
        self._queue = queue.Queue(maxsize=200)
        self.api_no_connection = TdxExHq_API()
        self._api_worker = Thread(target=self.api_worker, args=(), name='API Worker')
        self._api_worker.start()
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(self.thread_num)
        self.sleep_time = sleep_time

    def __getattr__(self, item):
        try:
            api = self.get_available()
            func = api.__getattribute__(item)
            def wrapper(*args, **kwargs):
                f = self.executor.submit(func, *args, **kwargs)
                try:
                    result = f.result()
                    if result is not None and len(result) > 0:
                        self._queue.put(api)
                    return result
                except Exception as e:
                    raise e
            return wrapper
        except Exception as e:
            raise e

    def _queue_clean(self):
        self._queue = queue.Queue(maxsize=200)

    def _test_speed(self, ip, port=7727):
        api = TdxExHq_API(raise_exception=True, auto_retry=False)
        _time = datetime.datetime.now()
        try:
            with api.connect(ip, port, time_out=1):
                if len(api.get_instrument_info(0)) > 0:
                    return (datetime.datetime.now() - _time).total_seconds()
                else:
                    return datetime.timedelta(9, 9, 0).total_seconds()
        except Exception as e:
            return datetime.timedelta(9, 9, 0).total_seconds()

    @property
    def ipsize(self):
        return self._queue.qsize()

    @property
    def api(self):
        return self.get_available()

    def get_available(self):
        if self._queue.empty() is False:
            return self._queue.get_nowait()
        else:
            Timer(0, self.api_worker).start()
            return self._queue.get()

    def api_worker(self):
        if self._queue.qsize() < 80:
            for item in future_ip_list:
                if self._queue.full():
                    break
                _sec = self._test_speed(ip=item['ip'], port=item['port'])
                if _sec < self.timeout * 3:
                    try:
                        api = TdxExHq_API(multithread=True, heartbeat=True)
                        api.connect(ip=item['ip'], port=item['port'], time_out=self.timeout * 2)
                        self._queue.put(api)
                    except:
                        pass


app = FastAPI()

def ex_get_markets():
    return TdxExHqExecutor().get_markets()

@app.get("/ex/get_markets")
async def _ex_get_markets():
    return ex_get_markets()

def ex_get_instrument_count():
    return TdxExHqExecutor().get_instrument_count()

@app.get("/ex/get_instrument_count")
async def _ex_get_instrument_count():
    return ex_get_instrument_count()

def ex_get_instrument_quote(market: int, code: str):
    return TdxExHqExecutor().get_instrument_quote(market, code)

@app.get("/ex/get_instrument_quote")
async def _ex_get_instrument_quote(market: int, code: str):
    return ex_get_instrument_quote(market, code)

def ex_get_instrument_bars(category: int, market: int, code: str, start: int=0, count: int=700):
    return TdxExHqExecutor().get_instrument_bars(category, market, code, start, count)

@app.get("/ex/get_instrument_bars")
async def _ex_get_instrument_bars(category: int, market: int, code: str, start: int=0, count: int=700):
    return ex_get_instrument_bars(category, market, code, start, count)

def ex_get_minute_time_data(market: int, code: str):
    return TdxExHqExecutor().get_minute_time_data(market, code)

@app.get("/ex/get_minute_time_data")
async def _ex_get_minute_time_data(market: int, code: str):
    return ex_get_minute_time_data(market, code)

def ex_get_history_minute_time_data(market: int, code: str, date: int):
    return TdxExHqExecutor().get_history_minute_time_data(market, code, date)

@app.get("/ex/get_history_minute_time_data")
async def _ex_get_history_minute_time_data(market: int, code: str, date: int):
    return ex_get_history_minute_time_data(market, code, date)

def ex_get_transaction_data(market: int, code: str, start: int=0, count: int=1800):
    return TdxExHqExecutor().get_transaction_data(market, code, start, count)

@app.get("/ex/get_transaction_data")
async def _ex_get_transaction_data(market: int, code: str, start: int=0, count: int=1800):
    return ex_get_transaction_data(market, code, start, count)

def ex_get_history_transaction_data(market: int, code: str, date: int, start: int=0, count: int=1800):
    return TdxExHqExecutor().get_history_transaction_data(market, code, date, start, count)

@app.get("/ex/get_history_transaction_data")
async def _ex_get_history_transaction_data(market: int, code: str, date: int, start: int=0, count: int=1800):
    return ex_get_history_transaction_data(market, code, date, start, count)

def ex_get_history_instrument_bars_range(market: int, code: str, start: int, end: int):
    return TdxExHqExecutor().get_history_instrument_bars_range(market, code, start, end)

@app.get("/ex/get_history_instrument_bars_range")
async def _ex_get_history_instrument_bars_range(market: int, code: str, start: int, end: int):
    return ex_get_history_instrument_bars_range(market, code, start, end)

def ex_get_instrument_info(start: int, count: int=100):
    return TdxExHqExecutor().get_instrument_info(start, count)

@app.get("/ex/get_instrument_info")
async def _ex_get_instrument_info(start: int, count: int=100):
    return ex_get_instrument_info(start, count)

def ex_get_instrument_quote_list(market: int, category: int, start: int=0, count: int=80):
    return TdxExHqExecutor().get_instrument_quote_list(market, category, start, count)

@app.get("/ex/get_instrument_quote_list")
async def _ex_get_instrument_quote_list(market: int, category: int, start: int=0, count: int=80):
    return ex_get_instrument_quote_list(market, category, start, count)

if __name__ == "__main__":
    uvicorn.run("pychanlun.gateway.tdxhq:app", host="0.0.0.0", port=5001)
