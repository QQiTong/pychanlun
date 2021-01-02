# -*- coding: utf-8 -*-

import os
from QUANTAXIS.QASU.main import (QA_SU_save_stock_list, QA_SU_save_stock_block, QA_SU_save_stock_day,
                                 QA_SU_save_stock_min,
                                 QA_SU_save_index_list, QA_SU_save_index_day, QA_SU_save_index_min,
                                 QA_SU_save_etf_list, QA_SU_save_etf_day, QA_SU_save_etf_min,
                                 QA_SU_save_future_list, QA_SU_save_future_day_all, QA_SU_save_future_min_all)
from pychanlun.select import a_stock_signal
from pychanlun.monitor import a_stock_tdx


def run(**kwargs):
    QA_SU_save_stock_list('tdx')
    QA_SU_save_stock_block('tdx')
    QA_SU_save_stock_day('tdx')
    QA_SU_save_stock_min('tdx')
    QA_SU_save_index_list('tdx')
    QA_SU_save_index_day('tdx')
    QA_SU_save_index_min('tdx')
    QA_SU_save_etf_list('tdx')
    QA_SU_save_etf_day('tdx')
    QA_SU_save_etf_min('tdx')
    QA_SU_save_future_list('tdx')
    QA_SU_save_future_day_all('tdx')
    QA_SU_save_future_min_all('tdx')

    a_stock_signal.run(**{})
    a_stock_tdx.run(**{"loop": False})
    if kwargs.get("auto_shutdown", False):
        os.system("shutdown -s -f -t 300")


if __name__ == '__main__':
    run()
