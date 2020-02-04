# -*- coding: utf-8 -*-

import os
import logging
from logging import handlers
from rqdatac import init

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

init(
    'license',
    'R-yCtlfkzEy5pJSHCL3BIuraslQ-bE4Fh11pt2_iPkpl09pI0rDCvhQ7CEQ0nEqbZ5tcEt-Bs1YWfR3RE9IxRbgJpU9Kjli3oOMOXEpEMy5spOZpmf8Gp9DVgdysfNEga4QxX7Wy-SY--_Qrvtq-iUHmmRHVRn3_RYS0Zp21TIY=d1ew3T3pkd68D5yrr2OoLr7uBF6A3AekruZMo-KhGPqaYFMFOTztTeFJmnY-N3lCPFEhm673p1BZIZDrN_pC_njhwl-r5jZnAMptcHM0Ge1FK6Pz7XiauJGE5KBNvHjLHcFtvlAGtvh83sjm70tTmVqfFHETKfUVpz2ogbCzCAo=',
    ('rqdatad-pro.ricequant.com', 16011)
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(threadName)s %(levelname)s %(message)s')
# logger = logging.getLogger()
# logfile = os.path.join(BASE_DIR, "logs\pychanlun.log")
# fh = handlers.RotatingFileHandler(filename=logfile, maxBytes=10*1024*1024, backupCount=5)
# logger.addHandler(fh)
