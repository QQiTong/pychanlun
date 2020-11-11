# -*- coding: utf-8 -*-

import os
import sys
import logging
from pychanlun import server

logging.disable(logging.INFO)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

server.run()
