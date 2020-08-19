# -*- coding: utf-8 -*-

import os
from QUANTAXIS.QASU.main import (QA_SU_save_stock_block, QA_SU_save_stock_day,
                                 QA_SU_save_stock_list, QA_SU_save_stock_min)
from pychanlun.select import a_stock_signal
from pychanlun.monitor import a_stock_tdx


def run(**kwargs):
    QA_SU_save_stock_list('tdx')
    QA_SU_save_stock_block('tdx')
    QA_SU_save_stock_day('tdx')
    QA_SU_save_stock_min('tdx')
    a_stock_signal.run(**{})
    a_stock_tdx.run(**{"loop": False})
    os.system("shutdown -s -f -t 60")


if __name__ == '__main__':
    run()
