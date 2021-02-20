# -*- coding: utf-8 -*-

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
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
    'symbolList': [
        # 第一组  28个
        # 黑色系
        "RB",
        "HC",
        "I",
        "J",
        "JM",
        # 金属类
        "AG",
        "AU",
        "NI",
        "ZN",
        # 化工系
        "RU",
        "FU",
        "BU",
        "MA",
        "TA",
        "PP",
        "EG",
        "EB",
        "L",
        # "PG",
        # 农产品
        "CF",
        "SR",
        "AP",
        "JD",
        "A",
        "M",
        # "RM",
        # 食用油
        "Y",
        "P",
        # "OI",

        # "IC",
        # "IF",
        # "IH",

        #   第二组 新增品种 15
        #     "AL",
        #     "SN",
        #     "PB",
        #     "SM",
        "SF",

        # "B",
        "C",
        # "CS",
        # "CJ",
        # "SP",

        "FG",
        "SA",
        "ZC",
        "UR",
        "V",
    ],
    # 指数列表
    'symbolListIndex': [
        # 第一组  28个
        # 黑色系
        "RB99",
        "HC99",
        "I99",
        "J99",
        "JM99",
        # 金属类
        "AG99",
        "AU99",
        "NI99",
        "ZN99",
        # 化工系
        "RU99",
        "FU99",
        "BU99",
        "MA99",
        "TA99",
        "PP99",
        "EG99",
        "EB99",
        "L99",
        # "PG99",
        # 农产品
        "CF99",
        "SR99",
        "AP99",
        "JD99",
        "A99",
        "M99",
        # "RM99",
        # 食用油
        "Y99",
        "P99",
        # "OI99",

        # "IC99",
        # "IF99",
        # "IH99",

        #   第二组 新增品种 15
        #     "AL99",
        #     "SN99",
        #     "PB99",
        #     "SM99",
        # "SF99",

        # "B99",
        "C99",
        # "CS99",
        # "CJ99",
        # "SP99",

        "FG99",
        "SA99",
        "ZC99",
        "UR99",
        "V99",
    ],
    # 华安期货是在标准保证金基础上加1个点，这个可以找期货公司调整 b
    'margin_rate_company': 0.01,
    # 商品期货保证金率一般固定，只有过节会变下。因为换合约期间需要拿到老合约保证金率，因此保存起来
    'futureConfig': {
        'RB': {'margin_rate': 0.09, 'contract_multiplier': 10},
        'HC': {'margin_rate': 0.09, 'contract_multiplier': 10},
        'I': {'margin_rate': 0.08, 'contract_multiplier': 100},
        'J': {'margin_rate': 0.08, 'contract_multiplier': 100},
        'JM': {'margin_rate': 0.08, 'contract_multiplier': 60},
        # 郑煤
        'ZC': {'margin_rate': 0.05, 'contract_multiplier': 100},
        # 锰硅
        'SM': {'margin_rate': 0.07, 'contract_multiplier': 5},
        # 硅铁
        'SF': {'margin_rate': 0.07, 'contract_multiplier': 5},

        'RU': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'FU': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'BU': {'margin_rate': 0.11, 'contract_multiplier': 10},

        'MA': {'margin_rate': 0.07, 'contract_multiplier': 10},
        'TA': {'margin_rate': 0.07, 'contract_multiplier': 5},

        'EG': {'margin_rate': 0.11, 'contract_multiplier': 10},
        # 苯乙烯
        'EB': {'margin_rate': 0.12, 'contract_multiplier': 5},
        # 聚丙烯
        'PP': {'margin_rate': 0.11, 'contract_multiplier': 5},
        # 聚乙烯
        'L': {'margin_rate': 0.11, 'contract_multiplier': 5},
        # 聚氯乙烯
        'V': {'margin_rate': 0.09, 'contract_multiplier': 5},
        'AU': {'margin_rate': 0.08, 'contract_multiplier': 1000},
        'AG': {'margin_rate': 0.12, 'contract_multiplier': 15},
        'NI': {'margin_rate': 0.1, 'contract_multiplier': 1},
        'ZN': {'margin_rate': 0.1, 'contract_multiplier': 5},
        # 'SP': {'margin_rate': 0.08, 'contract_multiplier': 10},
        # 'CU': {'margin_rate': 0.1, 'contract_multiplier': 5},

        # 沪铝
        # 'AL': {'margin_rate': 0.1, 'contract_multiplier': 5},
        # 沪锡
        # 'SN': {'margin_rate': 0.1, 'contract_multiplier': 1},
        # 沪铅
        # 'PB': {'margin_rate': 0.1, 'contract_multiplier': 5},

        'CF': {'margin_rate': 0.07, 'contract_multiplier': 5},
        'SR': {'margin_rate': 0.05, 'contract_multiplier': 10},
        # 'OI': {'margin_rate': 0.06, 'contract_multiplier': 10},
        # 'RM': {'margin_rate': 0.06, 'contract_multiplier': 10},
        'AP': {'margin_rate': 0.08, 'contract_multiplier': 10},
        # 'CJ': {'margin_rate': 0.08, 'contract_multiplier': 5},
        # 玻璃
        'FG': {'margin_rate': 0.06, 'contract_multiplier': 20},
        # 纯碱
        'SA': {'margin_rate': 0.06, 'contract_multiplier': 20},

        # 尿素
        'UR': {'margin_rate': 0.05, 'contract_multiplier': 20},

        'M': {'margin_rate': 0.08, 'contract_multiplier': 10},
        'P': {'margin_rate': 0.08, 'contract_multiplier': 10},
        'Y': {'margin_rate': 0.08, 'contract_multiplier': 10},
        'JD': {'margin_rate': 0.09, 'contract_multiplier': 10},
        # 'PG': {'margin_rate': 0.11, 'contract_multiplier': 20},
        # 豆一
        'A': {'margin_rate': 0.08, 'contract_multiplier': 10},

        # 豆二
        # 'B': {'margin_rate': 0.08, 'contract_multiplier': 10},
        # 玉米
        'C': {'margin_rate': 0.07, 'contract_multiplier': 10},
        # 淀粉
        # 'CS': {'margin_rate': 0.07, 'contract_multiplier': 10},

        # 'IC': {'margin_rate': 0.12, 'contract_multiplier': 200},
        # 'IF': {'margin_rate': 0.10, 'contract_multiplier': 300},
        # 'IH': {'margin_rate': 0.10, 'contract_multiplier': 300},
        'BTC': {'margin_rate': 0.05, 'contract_multiplier': 1},
        # 外盘
        'CL': {'margin_rate': 0.16, 'contract_multiplier': 500},  # 8:30 -14:00 0.1      其它时间 0.15       11756
        'GC': {'margin_rate': 0.07, 'contract_multiplier': 10},  # 8:30 -14:00 0.02   其它时间 0.03         10065
        'SI': {'margin_rate': 0.14, 'contract_multiplier': 5000},  # 18:30 -14:00 0.04   其它时间 0.06       10271
        'HG': {'margin_rate': 0.06, 'contract_multiplier': 25000},  # 18:30 -14:00 0.04   其它时间 0.06       10271
        'NID': {'margin_rate': 0.1, 'contract_multiplier': 1},
        'ZSD': {'margin_rate': 0.1, 'contract_multiplier': 1},
        # 'CN': {'margin_rate': 0.09, 'contract_multiplier': 1},  # 18:30 -14:00 0.04   其它时间 0.06          1045

        'S': {'margin_rate': 0.03, 'contract_multiplier': 50},  # 2314
        # 'SM': {'margin_rate': 0.04, 'contract_multiplier': 100},  # 2062
        'BO': {'margin_rate': 0.04, 'contract_multiplier': 600},  # 935
        'FCPO': {'margin_rate': 0.1, 'contract_multiplier': 1},
        'CT': {'margin_rate': 0.1, 'contract_multiplier': 1},
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
    'periodList': [
        '1m',
        '3m',
        '5m',
        '15m',
        '30m',
        '60m',
        '180m',
        '1d',
        '1w'
    ],
    # 外盘期货品种
    # CL:原油; GC:黄金;SI:白银; CT:棉花;S:大豆;SM:豆粕; BO:豆油;NID:伦镍; ZSD:伦锌;HG:美铜
    # YM:道琼斯 CN:A50 ;FCPO:马棕榈
    # wshq 'SB'
    # 'global_future_symbol': ['CL', 'GC', 'SI', 'YM', 'NQ', 'ES', 'CN', 'ZS', 'ZM', 'ZL', 'NID', 'ZSD'],
    # 新浪外盘品种名'SM',
    'global_future_symbol': ['CL', 'GC', 'SI', 'HG', 'NID', 'ZSD', 'S',  'BO', 'FCPO', 'CT'],
    # 美国股票
    'global_stock_symbol': ['AAPL', 'MSFT', 'GOOG', 'FB', 'AMZN', 'NFLX', 'NVDA', 'AMD'],
    # wshq
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
    },
    'digit_coin_symbol': ['BTC'],
    'digit_coin_symbol_info': [{
        'contract_multiplier': 1,
        'de_listed_date': 'forever',
        'exchange': 'OKEX',
        'listed_date': 'forever',
        'margin_rate': 0.05,
        'market_tplus': 0,
        'maturity_date': 'forever',
        'order_book_id': 'BTC',
        'round_lot': 1,
        'symbol': '比特币',
        'trading_hours': '7*24',
        'type': 'Future',
        'underlying_order_book_id': 'null',
        'underlying_symbol': 'BTC',
        'feeRate': 0.012
    }],

    'global_future_symbol_info': [
        {
            'contract_multiplier': 500,
            'exchange': '美国',
            'margin_rate': 0.16,
            'order_book_id': 'CL',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 10,
            'exchange': '美国',
            'margin_rate': 0.07,
            'order_book_id': 'GC',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 5000,
            'exchange': '美国',
            'margin_rate': 0.14,
            'order_book_id': 'SI',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 25000,
            'exchange': '美铜',
            'margin_rate': 0.06,
            'order_book_id': 'HG',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '新加坡',
        #     'margin_rate': 0.09,
        #     'order_book_id': 'CN',
        #     'trading_hours': '7*24',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 0.5,
        #     'exchange': '美国',
        #     'margin_rate': 0.13,
        #     'order_book_id': 'YM',
        #     'trading_hours': '7*24',
        #     'type': 'future',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 5,
        #     'exchange': '美国',
        #     'margin_rate': 0.086,
        #     'order_book_id': 'ES',
        #     'trading_hours': '7*24',
        #     'type': 'future',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 2,
        #     'exchange': '美国',
        #     'margin_rate': 0.086,
        #     'order_book_id': 'NQ',
        #     'trading_hours': '7*24',
        #     'type': 'future',
        #     'feeRate': 0.012
        # },
        {
            'contract_multiplier': 1,
            'exchange': '伦敦',
            'margin_rate': 0.1,
            'order_book_id': 'NID',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 1,
            'exchange': '伦敦',
            'margin_rate': 0.1,
            'order_book_id': 'ZSD',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },

        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 0.1,
        #     'order_book_id': 'SB',
        #     'trading_hours': '7*24',
        #     'type': 'future',
        #     'feeRate': 0.012
        # },
        {
            'contract_multiplier': 50,
            'exchange': '美豆',
            'margin_rate': 0.03,
            'order_book_id': 'S',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        # {
        #     'contract_multiplier': 50,
        #     'exchange': '美玉米',
        #     'margin_rate': 0.06,
        #     'order_book_id': 'C',
        #     'trading_hours': '7*24',
        #     'type': 'future',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 100,
        #     'exchange': '美豆粕',
        #     'margin_rate': 0.04,
        #     'order_book_id': 'SM',
        #     'trading_hours': '7*24',
        #     'type': 'future',
        #     'feeRate': 0.012
        # },
        {
            'contract_multiplier': 600,
            'exchange': '美豆油',
            'margin_rate': 0.04,
            'order_book_id': 'BO',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 1,
            'exchange': '美棉',
            'margin_rate': 0.1,
            'order_book_id': 'CT',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 1,
            'exchange': '马来西亚',
            'margin_rate': 0.1,
            'order_book_id': 'FCPO',
            'trading_hours': '7*24',
            'type': 'stock',
            'feeRate': 0.012
        },
    ],
    # 内盘期货信息列表
    'future_symbol_info': [
        # 黑色板块
        {
            'order_book_id': 'RB99',
            'contract_multiplier': 10,
            'margin_rate': 0.09,
        },
        {
            'order_book_id': 'HC99',
            'contract_multiplier': 10,
            'margin_rate': 0.09,
        },
        {
            'order_book_id': 'I99',
            'contract_multiplier': 100,
            'margin_rate': 0.08,
        },
        {
            'order_book_id': 'J99',
            'contract_multiplier': 100,
            'margin_rate': 0.08,
        },
        {
            'order_book_id': 'JM99',
            'contract_multiplier': 60,
            'margin_rate': 0.08,
        },

        # 动力煤
        {
            'order_book_id': 'ZC99',
            'contract_multiplier': 100,
            'margin_rate': 0.05,
        },
        # 锰硅
        {
            'order_book_id': 'SM99',
            'contract_multiplier': 5,
            'margin_rate': 0.07,
        },
        # 硅铁
        {
            'order_book_id': 'SF99',
            'contract_multiplier': 5,
            'margin_rate': 0.07,
        },

        # 化工板块
        {
            'order_book_id': 'RU99',
            'contract_multiplier': 10,
            'margin_rate': 0.11,
        },
        {
            'order_book_id': 'FU99',
            'contract_multiplier': 10,
            'margin_rate': 0.11,
        },
        {
            'order_book_id': 'BU99',
            'contract_multiplier': 10,
            'margin_rate': 0.11,
        },

        {
            'order_book_id': 'MA99',
            'contract_multiplier': 10,
            'margin_rate': 0.07,
        },
        {
            'order_book_id': 'TA99',
            'contract_multiplier': 5,
            'margin_rate': 0.07,
        },
        {
            'order_book_id': 'EG99',
            'contract_multiplier': 10,
            'margin_rate': 0.11,
        },
        # 苯乙烯
        {
            'order_book_id': 'EB99',
            'contract_multiplier': 5,
            'margin_rate': 0.12,
        },
        # 聚丙烯
        {
            'order_book_id': 'PP99',
            'contract_multiplier': 5,
            'margin_rate': 0.12,
        },
        # 聚乙烯
        {
            'order_book_id': 'L99',
            'contract_multiplier': 5,
            'margin_rate': 0.11,
        },
        # 聚氯乙烯
        {
            'order_book_id': 'V99',
            'contract_multiplier': 5,
            'margin_rate': 0.09,
        },
        {
            'order_book_id': 'AU99',
            'contract_multiplier': 1000,
            'margin_rate': 0.08,
        },
        {
            'order_book_id': 'AG99',
            'contract_multiplier': 15,
            'margin_rate': 0.12,
        },
        {
            'order_book_id': 'NI99',
            'contract_multiplier': 1,
            'margin_rate': 0.1,
        },
        {
            'order_book_id': 'ZN99',
            'contract_multiplier': 5,
            'margin_rate': 0.1,
        },
        # {
        #     'order_book_id': 'SP99',
        #     'contract_multiplier': 10,
        #     'margin_rate': 0.08,
        # },
        # {
        #     'order_book_id': 'CU99',
        #     'contract_multiplier': 5,
        #     'margin_rate': 0.1,
        # },
        # {
        #     'order_book_id': 'AL99',
        #     'contract_multiplier': 5,
        #     'margin_rate': 0.1,
        # },
        # {
        #     'order_book_id': 'SN99',#沪锡
        #     'contract_multiplier': 1,
        #     'margin_rate': 0.1,
        # },
        # {
        #     'order_book_id': 'PB99',#沪铅
        #     'contract_multiplier': 5,
        #     'margin_rate': 0.1,
        # },

        # 郑商所

        {
            'order_book_id': 'CF99',
            'contract_multiplier': 5,
            'margin_rate': 0.07,
        },
        {
            'order_book_id': 'SR99',
            'contract_multiplier': 10,
            'margin_rate': 0.05,
        },
        # {
        #     'order_book_id': 'OI99',
        #     'contract_multiplier': 10,
        #     'margin_rate': 0.06,
        # },
        # {
        #     'order_book_id': 'RM99',
        #     'contract_multiplier': 10,
        #     'margin_rate': 0.06,
        # },
        {
            'order_book_id': 'AP99',
            'contract_multiplier': 10,
            'margin_rate': 0.08,
        },
        # {
        #     'order_book_id': 'CJ99',
        #     'contract_multiplier': 5,
        #     'margin_rate': 0.08,
        # },
        # 玻璃
        {
            'order_book_id': 'FG99',
            'contract_multiplier': 20,
            'margin_rate': 0.06,
        },
        # 纯碱
        {
            'order_book_id': 'SA99',
            'contract_multiplier': 20,
            'margin_rate': 0.06,
        },
        # 尿素
        {
            'order_book_id': 'UR99',
            'contract_multiplier': 20,
            'margin_rate': 0.05,
        },
        # 大商所
        {
            'order_book_id': 'M99',
            'contract_multiplier': 10,
            'margin_rate': 0.08,
        },

        {
            'order_book_id': 'P99',
            'contract_multiplier': 10,
            'margin_rate': 0.08,
        },
        {
            'order_book_id': 'Y99',
            'contract_multiplier': 10,
            'margin_rate': 0.08,
        },
        # {
        #     'order_book_id': 'JD99',
        #     'contract_multiplier': 10,
        #     'margin_rate': 0.09,
        # },
        #  {
        #     'order_book_id': 'PG99',
        #     'contract_multiplier': 20,
        #     'margin_rate': 0.11,
        # },

        {
            'order_book_id': 'A99',
            'contract_multiplier': 10,
            'margin_rate': 0.08,
        },
        # {
        #             'order_book_id': 'B99',
        #             'contract_multiplier': 10,
        #             'margin_rate': 0.08,
        #         },
        {
            'order_book_id': 'C99',
            'contract_multiplier': 10,
            'margin_rate': 0.07,
        },
        # 淀粉
        # {
        #             'order_book_id': 'CS99',
        #             'contract_multiplier': 10,
        #             'margin_rate': 0.07,
        #         },

        # {
        #             'order_book_id': 'IC99',
        #             'contract_multiplier': 200,
        #             'margin_rate': 0.12,
        #         },
        # {
        #             'order_book_id': 'IF99',
        #             'contract_multiplier': 300,
        #             'margin_rate': 0.10,
        #         },
        # {
        #             'order_book_id': 'IH99',
        #             'contract_multiplier': 300,
        #             'margin_rate': 0.10,
        #         },
        # {
        #             'order_book_id': 'BTC',
        #             'contract_multiplier': 1,
        #             'margin_rate': 0.05,
        #         },
    ]
}
cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
