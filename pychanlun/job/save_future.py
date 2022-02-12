# -*- coding: utf-8 -*-

import os
from QUANTAXIS.QASU.main import (QA_SU_save_future_list, QA_SU_save_future_day_all, QA_SU_save_future_min_all)
from pychanlun.select import a_stock_signal
from pychanlun.monitor import a_stock_tdx


def run(**kwargs):
    QA_SU_save_future_list('tdx')
    QA_SU_save_future_day_all('tdx')
    QA_SU_save_future_min_all('tdx')
    if kwargs.get("auto_shutdown", False):
        os.system("shutdown -s -f -t 300")


if __name__ == '__main__':
    run()
