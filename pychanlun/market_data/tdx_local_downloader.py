# -*- coding: utf-8 -*-

import os
import logging
from pytdx.reader import TdxLCMinBarReader, TdxFileNotFoundException
import re

def run(**kwargs):
    logger = logging.getLogger()
    tdx_home = os.environ.get("TDX_HOME")
    if tdx_home is None:
        logger.error("没有指定通达信安装目录环境遍历（TDX_HOME）")
        return

    for subdir in ["sh", "sz"]:
        path = os.path.join(tdx_home, "vipdoc\\%s\\fzline" % subdir)
        files = os.listdir(path)
        reader = TdxLCMinBarReader()
        for filename in files:
            code = None
            if subdir == "sh":
                match = re.match("(sh)6(\\d{5})", filename, re.I)
                if match is not None:
                    code = match.group()
            elif subdir == "sz":
                match = re.match("(sz)(00|30)(\\d{4})", filename, re.I)
                if match is not None:
                    code = match.group()
            filepath = os.path.join(path, filename)
            if code is not None:
                df = reader.get_df(filepath)
                print(df)
                break
        break
