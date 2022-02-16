'''
2022年起 RQdata限制每日1G流量,3线程,同一时间单用户登陆
测试3线程采集
'''
from loguru import logger
import signal
import threading
import traceback
import rqdatac as rq

symbol_list = ["RB", "HC", "I", "J", "JM", "AG", "AU", "NI", "ZN", "RU", "FU", "BU", "MA", "TA", "PP", "EG", "EB", "L",
               "CF", "SR", "AP", "JD", "A", "M", "Y", "P", "SF", "C", "FG", "SA", "ZC", "UR", "V"]
is_run = True
def thread1():
    try:
        dominant_symbol_list = []
        for i in range(len(symbol_list)):
            df = rq.futures.get_dominant(symbol_list[i], start_date=None, end_date=None, rule=0)
            dominant_symbol = df[-1]
            dominant_symbol_list.append(dominant_symbol)
        while is_run:
            for i in range(len(dominant_symbol_list)):
                df = rq.current_minute(dominant_symbol_list[i])
                print("线程1 获取主力合约数据", df)
            if not is_run:
                break
    except BaseException as e:
        logger.error("Error Occurred: {0}".format(traceback.format_exc()))


def thread2():
    try:
        while is_run:
            for i in range(len(symbol_list)):
                df = rq.current_minute(symbol_list[i] + "88")
                print("线程2 获取主连合约数据", df)
            if not is_run:
                break
    except BaseException as e:
        logger.error("Error Occurred: {0}".format(traceback.format_exc()))


def thread3():
    try:
        while is_run:
            for i in range(len(symbol_list)):
                df = rq.current_minute(symbol_list[i] + "99")
                print("线程3 获取指数合约数据", df)
            if not is_run:
                break
    except BaseException as e:
        logger.error("Error Occurred: {0}".format(traceback.format_exc()))


def run(**kwargs):
    signal.signal(signal.SIGINT, signal_handler)
    thread_list = [threading.Thread(target=thread1), threading.Thread(target=thread2), threading.Thread(target=thread3)]
    for thread in thread_list:
        thread.start()
    while True:
        for thread in thread_list:
            if thread.is_alive():
                break
        else:
            break


def signal_handler(signalnum, frame):
    logger.info("正在停止程序。")
    global is_run
    is_run = False


if __name__ == '__main__':
    run()
