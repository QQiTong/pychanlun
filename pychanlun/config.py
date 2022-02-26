# -*- coding: utf-8 -*-

import os
import sys
import pytz
from dynaconf import Dynaconf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # freshquant所在目录
EXE_DIR = os.path.split(os.path.realpath(sys.argv[0]))[0]  # 程序或脚本所在目录
CWD_DIR = os.getcwd()  # 执行程序或脚本的目录


class Config:
    BASE_DIR = BASE_DIR
    EXE_DIR = EXE_DIR
    CWD_DIR = CWD_DIR
    TIMEZONE = 'Asia/Shanghai'
    TZ = pytz.timezone(TIMEZONE)
    DT_FORMAT_FULL = "%Y-%m-%d %H:%M:%S"
    DT_FORMAT_DAY = "%Y-%m-%d"
    DT_FORMAT_M = "%Y-%m-%d %H:%M"
    FUTURE_OHLC = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'position': 'sum', 'amount': 'sum'}

    PROXIES = {
        "http": "socks5://127.0.0.1:10808",
        "https": "socks5://127.0.0.1:10808"
    }


class DevelopmentConfig(Config):
    # 局域网2台电脑公用数据库
    MONGODB_SETTINGS = {
        'url': os.environ.get('PYCHANLUN_MONGO_URL', 'mongodb://localhost:27017/pychanlun')
    }
    pass


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'url': os.environ.get('PYCHANLUN_MONGO_URL', 'mongodb://localhost:27017/pychanlun')
    }
    pass


config = {
    'default': DevelopmentConfig,
    'production': ProductionConfig,
    # 华安期货是在标准保证金基础上加1个点，这个可以找期货公司调整 b
    'margin_rate_company': 0.01,
    # 商品期货保证金率一般固定，只有过节会变下。因为换合约期间需要拿到老合约保证金率，因此保存起来
    'future_config': {
        'RB': {'order_book_id': 'RBL9', 'margin_rate': 0.09, 'contract_multiplier': 10},
        'HC': {'order_book_id': 'HCL9', 'margin_rate': 0.09, 'contract_multiplier': 10},
        'I': {'order_book_id': 'IL9', 'margin_rate': 0.08, 'contract_multiplier': 100},
        'J': {'order_book_id': 'JL9', 'margin_rate': 0.08, 'contract_multiplier': 100},
        'JM': {'order_book_id': 'JML9', 'margin_rate': 0.08, 'contract_multiplier': 60},
        # 郑煤
        'ZC': {'order_book_id': 'ZCL9','margin_rate': 0.5, 'contract_multiplier': 100},
        # 锰硅
        'SM': {'order_book_id': 'SML9','margin_rate': 0.07, 'contract_multiplier': 5},
        # 硅铁
        'SF': {'order_book_id': 'SFL9','margin_rate': 0.07, 'contract_multiplier': 5},

        'RU': {'order_book_id': 'RUL9','margin_rate': 0.11, 'contract_multiplier': 10},
        'FU': {'order_book_id': 'FUL9','margin_rate': 0.11, 'contract_multiplier': 10},
        'BU': {'order_book_id': 'BUL9','margin_rate': 0.11, 'contract_multiplier': 10},

        'MA': {'order_book_id': 'MAL9','margin_rate': 0.07, 'contract_multiplier': 10},
        'TA': {'order_book_id': 'TAL9','margin_rate': 0.07, 'contract_multiplier': 5},

        'EG': {'order_book_id': 'EGL9','margin_rate': 0.11, 'contract_multiplier': 10},
        # 苯乙烯
        'EB': {'order_book_id': 'EBL9','margin_rate': 0.12, 'contract_multiplier': 5},
        # 聚丙烯
        'PP': {'order_book_id': 'PPL9','margin_rate': 0.11, 'contract_multiplier': 5},
        # 聚乙烯
        'L': {'order_book_id': 'LL9','margin_rate': 0.11, 'contract_multiplier': 5},
        # 聚氯乙烯
        'V': {'order_book_id': 'VL9','margin_rate': 0.09, 'contract_multiplier': 5},
        'AU': {'order_book_id': 'AUL9','margin_rate': 0.08, 'contract_multiplier': 1000},
        'AG': {'order_book_id': 'AGL9','margin_rate': 0.12, 'contract_multiplier': 15},
        'NI': {'order_book_id': 'NIL9','margin_rate': 0.1, 'contract_multiplier': 1},
        'ZN': {'order_book_id': 'ZNL9','margin_rate': 0.1, 'contract_multiplier': 5},
        'SP': {'order_book_id': 'SPL9','margin_rate': 0.08, 'contract_multiplier': 10},
        'CU': {'order_book_id': 'CUL9','margin_rate': 0.1, 'contract_multiplier': 5},

        # 沪铝
        'AL': {'order_book_id': 'ALL9','margin_rate': 0.1, 'contract_multiplier': 5},
        # 沪锡
        'SN': {'order_book_id': 'SNL9','margin_rate': 0.1, 'contract_multiplier': 1},
        # 沪铅
        # 'PB': {'order_book_id': 'CL','margin_rate': 0.1, 'contract_multiplier': 5},

        'CF': {'order_book_id': 'CFL9','margin_rate': 0.07, 'contract_multiplier': 5},
        'SR': {'order_book_id': 'SRL9','margin_rate': 0.05, 'contract_multiplier': 10},
        # 'OI': {'order_book_id': 'CL','margin_rate': 0.06, 'contract_multiplier': 10},
        # 'RM': {'order_book_id': 'CL','margin_rate': 0.06, 'contract_multiplier': 10},
        'AP': {'order_book_id': 'APL9','margin_rate': 0.08, 'contract_multiplier': 10},
        # 'CJ': {'order_book_id': 'CL','margin_rate': 0.08, 'contract_multiplier': 5},
        # 玻璃
        'FG': {'order_book_id': 'FGL9','margin_rate': 0.06, 'contract_multiplier': 20},
        # 纯碱
        'SA': {'order_book_id': 'SAL9','margin_rate': 0.06, 'contract_multiplier': 20},

        # 尿素
        'UR': {'order_book_id': 'URL9','margin_rate': 0.05, 'contract_multiplier': 20},

        'M': {'order_book_id': 'ML9','margin_rate': 0.08, 'contract_multiplier': 10},
        'P': {'order_book_id': 'PL9','margin_rate': 0.08, 'contract_multiplier': 10},
        'Y': {'order_book_id': 'YL9','margin_rate': 0.08, 'contract_multiplier': 10},
        'JD': {'order_book_id': 'JDL9','margin_rate': 0.09, 'contract_multiplier': 10},
        'PG': {'order_book_id': 'PGL9','margin_rate': 0.11, 'contract_multiplier': 20},
        # 豆一
        'A': {'order_book_id': 'AL9','margin_rate': 0.08, 'contract_multiplier': 10},

        # 豆二
        # 'B': {'order_book_id': 'CL','margin_rate': 0.08, 'contract_multiplier': 10},
        # 玉米
        'C': {'order_book_id': 'CL9','margin_rate': 0.07, 'contract_multiplier': 10},
        # 淀粉
        # 'CS': {'order_book_id': 'CL','margin_rate': 0.07, 'contract_multiplier': 10},

        # 'IC': {'order_book_id': 'CL','margin_rate': 0.12, 'contract_multiplier': 200},
        # 'IF': {'order_book_id': 'CL','margin_rate': 0.10, 'contract_multiplier': 300},
        # 'IH': {'order_book_id': 'CL','margin_rate': 0.10, 'contract_multiplier': 300},
        # 外盘
        'CL': {'order_book_id': 'CL','margin_rate': 0.16, 'contract_multiplier': 500},  # 8:30 -14:00 0.1      其它时间 0.15       11756
        'GC': {'order_book_id': 'GC','margin_rate': 0.07, 'contract_multiplier': 10},  # 8:30 -14:00 0.02   其它时间 0.03         10065
        'SI': {'order_book_id': 'SI','margin_rate': 0.14, 'contract_multiplier': 5000},  # 18:30 -14:00 0.04   其它时间 0.06       10271
        'HG': {'order_book_id': 'HG','margin_rate': 0.06, 'contract_multiplier': 250},  # 由于新浪数据报价单位是美分 所以将乘数25000改成250
        'AHD': {'order_book_id': 'AHD','margin_rate': 0.1, 'contract_multiplier': 25},
        'NID': {'order_book_id': 'NID','margin_rate': 0.1, 'contract_multiplier': 6},
        'ZSD': {'order_book_id': 'ZSD','margin_rate': 0.1, 'contract_multiplier': 25},
        'SND': {'order_book_id': 'SND','margin_rate': 0.1, 'contract_multiplier': 5},
        'CN': {'order_book_id': 'CN','margin_rate': 0.09, 'contract_multiplier': 1},  # 18:30 -14:00 0.04   其它时间 0.06          1045

        'ZS': {'order_book_id': 'ZS','margin_rate': 0.03, 'contract_multiplier': 50},  # 美豆
        'ZM': {'order_book_id': 'ZM','margin_rate': 0.04, 'contract_multiplier': 100},  # 美豆粕
        'ZL': {'order_book_id': 'ZL','margin_rate': 0.04, 'contract_multiplier': 600},  # 美豆油
        'MZC': {'order_book_id': 'MZC','margin_rate': 0.06, 'contract_multiplier': 50},  # 美玉米
        'FCPO': {'order_book_id': 'FCPO','margin_rate': 0.1, 'contract_multiplier': 25},  # 马棕榈
        'CT': {'order_book_id': 'CT','margin_rate': 0.1, 'contract_multiplier': 100},  # 美棉花
        'BTC': {'order_book_id': 'BTC', 'margin_rate': 0.1, 'contract_multiplier': 1},

        # 'SB': {'margin_rate': 0.1, 'contract_multiplier': 1},
        # wshq
        # 'YM': {'margin_rate': 0.13, 'contract_multiplier': 0.5},  # 18:30 -14:00 0.04   其它时间 0.06          13200
        # 'ES': {'margin_rate': 0.086, 'contract_multiplier': 5},  # 18:30 -14:00 0.04   其它时间 0.06          13200
        # 'NQ': {'margin_rate': 0.086, 'contract_multiplier': 2},  # 18:30 -14:00 0.04   其它时间 0.06          13200

        # 'AAPL': {'margin_rate': 1, 'contract_multiplier': 1},
        # 'MSFT': {'margin_rate': 1, 'contract_multiplier': 1},
        # 'GOOG': {'margin_rate': 1, 'contract_multiplier': 1},
        # 'FB': {'margin_rate': 1, 'contract_multiplier': 1},
        # 'AMZN': {'margin_rate': 1, 'contract_multiplier': 1},
        # 'NFLX': {'margin_rate': 1, 'contract_multiplier': 1},
        # 'NVDA': {'margin_rate': 1, 'contract_multiplier': 1},
        # 'AMD': {'margin_rate': 1, 'contract_multiplier': 1},
        # 'ROKU': {'margin_rate': 1, 'contract_multiplier': 1},
    },
    # 外盘期货品种
    # CL:原油; GC:黄金;SI:白银; CT:棉花;S:大豆;SM:豆粕; BO:豆油;NID:伦镍; ZSD:伦锌;HG:美铜
    # YM:道琼斯 CN:A50 ;FCPO:马棕榈
    # 修正新浪外盘品种名 美豆 S->ZS,美豆粕 SM->ZM,美玉米ZC->MZC 马棕榈FCPO 美豆油BO->ZL
    'global_future_symbol_sina': ['CL', 'GC', 'SI', 'HG', 'AHD', 'NID', 'ZSD', 'SND', 'S', 'C', 'BO', 'FCPO', 'CT',
                                  "SM"],
    'global_future_symbol': ['CL', 'GC', 'SI', 'HG', 'AHD', 'NID', 'ZSD', 'SND', 'ZS', 'MZC', 'ZL', 'FCPO', 'CT', "ZM"],

    # 美国股票
    'global_stock_symbol': ['AAPL', 'MSFT', 'GOOG', 'FB', 'AMZN', 'NFLX', 'NVDA', 'AMD'],
    # wsstock.net
    'global_future_alias': {
        'NECLA0': 'CL',

        'CMGCA0': 'GC',
        'CMSIA0': 'SI',

        'CEYMA0': 'YM',
        'CEESA0': 'ES',
        'CENQA0': 'NQ',

        'WGCNA0': 'CN',

        'COZSA0': 'ZS',
        'COZMA0': 'ZM',
        'COZLA0': 'ZL',

        'IECTA0': 'CT',  # 美棉花
        'IESBA0': 'SB',  # 美糖

        'LENID3M': 'NID',  # 伦镍
        'LEZSD3M': 'ZSD',  # 伦锌
    }
}
cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
config_path = os.path.expanduser('~')
config_path = '{}{}{}'.format(config_path, os.sep, '.pychanlun')
settings = Dynaconf(
    settings_files=[
        os.path.join(BASE_DIR, "pychanlun.yaml"),
        os.path.join(BASE_DIR, "pychanlun.yml"),
        os.path.join(BASE_DIR, "pychanlun.json"),
        os.path.join(EXE_DIR, "pychanlun.yaml"),
        os.path.join(EXE_DIR, "pychanlun.yml"),
        os.path.join(EXE_DIR, "pychanlun.json"),
        os.path.join(config_path, "pychanlun.yaml"),
        os.path.join(config_path, "pychanlun.yml"),
        os.path.join(config_path, "pychanlun.json"),
        os.path.join(CWD_DIR, "pychanlun.yaml"),
        os.path.join(CWD_DIR, "pychanlun.yml"),
        os.path.join(CWD_DIR, "pychanlun.json"),
    ],
    includes=[
        os.path.join(BASE_DIR, "pychanlun_*.yaml"),
        os.path.join(BASE_DIR, "pychanlun_*.yml"),
        os.path.join(BASE_DIR, "pychanlun_*.json"),
        os.path.join(EXE_DIR, "pychanlun_*.yaml"),
        os.path.join(EXE_DIR, "pychanlun_*.yml"),
        os.path.join(EXE_DIR, "pychanlun_*.json"),
        os.path.join(config_path, "pychanlun_*.yaml"),
        os.path.join(config_path, "pychanlun_*.yml"),
        os.path.join(config_path, "pychanlun_*.json"),
        os.path.join(CWD_DIR, "pychanlun_*.yaml"),
        os.path.join(CWD_DIR, "pychanlun_*.yml"),
        os.path.join(CWD_DIR, "pychanlun_*.json")
    ],
    envvar_prefix="pychanlun",
)
