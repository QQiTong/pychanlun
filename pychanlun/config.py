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
        # 上期所
        "RB",
        "HC",
        "RU",
        "FU",
        "BU",
        # "AU",
        # "AG",
        "NI",
        # "ZN",
        # "SP",
        # 郑商所
        "MA",
        "TA",
        "CF",
        "SR",
        "OI",
        # "AP",
        # 大商所
        "J",
        "JM",
        "I",
        "RM",
        "M",
        "EG",
        "PP",
        "P",
        "Y",
        "PG"
        # "L",
        # "JD"
    ],
    # 华安期货是在标准保证金基础上加1个点，这个可以找期货公司调整
    'margin_rate_company': 0.01,
    # 商品期货保证金率一般固定，只有过节会变下。因为换合约期间需要拿到老合约保证金率，因此保存起来
    'futureConfig': {
        # 上期所
        'RB': {'margin_rate': 0.09, 'contract_multiplier': 10},
        'HC': {'margin_rate': 0.09, 'contract_multiplier': 10},
        'RU': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'FU': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'BU': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'AU': {'margin_rate': 0.08, 'contract_multiplier': 1000},
        'AG': {'margin_rate': 0.12, 'contract_multiplier': 15},
        'NI': {'margin_rate': 0.1, 'contract_multiplier': 1},
        'ZN': {'margin_rate': 0.1, 'contract_multiplier': 5},
        # 郑商所
        'MA': {'margin_rate': 0.07, 'contract_multiplier': 10},
        'TA': {'margin_rate': 0.07, 'contract_multiplier': 5},
        'CF': {'margin_rate': 0.07, 'contract_multiplier': 5},
        'SR': {'margin_rate': 0.05, 'contract_multiplier': 10},
        'OI': {'margin_rate': 0.065, 'contract_multiplier': 10},
        'RM': {'margin_rate': 0.06, 'contract_multiplier': 10},
        'AP': {'margin_rate': 0.08, 'contract_multiplier': 10},
        # 大商所
        'J': {'margin_rate': 0.08, 'contract_multiplier': 100},
        'JM': {'margin_rate': 0.08, 'contract_multiplier': 60},
        'I': {'margin_rate': 0.08, 'contract_multiplier': 100},
        'M': {'margin_rate': 0.08, 'contract_multiplier': 10},
        'EG': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'PP': {'margin_rate': 0.11, 'contract_multiplier': 5},
        'P': {'margin_rate': 0.08, 'contract_multiplier': 10},
        'Y': {'margin_rate': 0.08, 'contract_multiplier': 10},
        'JD': {'margin_rate': 0.09, 'contract_multiplier': 10},
        'PG': {'margin_rate': 0.08, 'contract_multiplier': 10},

        'BTC': {'margin_rate': 0.05, 'contract_multiplier': 1},
        # 外盘
        'CL': {'margin_rate': 0.56, 'contract_multiplier': 500},  # 8:30 -14:00 0.1      其它时间 0.15       11756
        'GC': {'margin_rate': 0.059, 'contract_multiplier': 10},  # 8:30 -14:00 0.02   其它时间 0.03         10065
        'SI': {'margin_rate': 0.13, 'contract_multiplier': 5000},  # 18:30 -14:00 0.04   其它时间 0.06       10271

        'CN': {'margin_rate': 0.09, 'contract_multiplier': 1},  # 18:30 -14:00 0.04   其它时间 0.06          1045

        'ZS': {'margin_rate': 0.056, 'contract_multiplier': 50},  # 2314
        'ZM': {'margin_rate': 0.07, 'contract_multiplier': 100},  # 2062
        'ZL': {'margin_rate': 0.06, 'contract_multiplier': 600},  # 935

        # 'NID': {'margin_rate': 0.1, 'contract_multiplier': 1},
        # 'CP': {'margin_rate': 0.1, 'contract_multiplier': 1},
        # 'CT': {'margin_rate': 0.1, 'contract_multiplier': 1},
        # wshq
        'YM': {'margin_rate': 0.13, 'contract_multiplier': 0.5},  # 18:30 -14:00 0.04   其它时间 0.06          13200
        'ES': {'margin_rate': 0.13, 'contract_multiplier': 0.5},  # 18:30 -14:00 0.04   其它时间 0.06          13200
        'NQ': {'margin_rate': 0.13, 'contract_multiplier': 0.5},  # 18:30 -14:00 0.04   其它时间 0.06          13200

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
        '240m',
        '1d',
        '1w'
    ],
    # 外盘期货品种
    # CL:原油; GC:黄金;SI:白银; CT:棉花;ZS:大豆;ZM:豆粕; ZL:豆油;NID:伦镍;
    # YM:道琼斯 CN:A50 CP:马棕榈
    'global_future_symbol_origin': ['@CL0W', '@GC0W', '@SI0W', '@YM0Y', 'CN0Y', '03NID', '@ZS0W', '@ZM0Y', '@ZL0W', 'CPO0W', 'CT0W'],
    # wshq
    'global_future_symbol': ['CL', 'GC', 'SI', 'YM', 'NQ', 'ES', 'CN','ZS', 'ZM', 'ZL'],
    # 美国股票
    'global_stock_symbol': ['AAPL', 'MSFT', 'GOOG', 'FB', 'AMZN', 'NFLX', 'NVDA', 'AMD'],
    # ldhq
    # 'global_future_alias': {
    #     '@CL0W': 'CL',
    #     '@GC0W': 'GC',
    #     '@SI0W': 'SI',
    #     '@YM0Y': 'YM',
    #     'CN0Y': 'CN',
    #     '03NID': 'NID',
    #     'CPO0W': 'CP',
    #     'CT0W': 'CT',
    #     '@ZS0W': 'ZS',
    #     '@ZM0Y': 'ZM',
    #     '@ZL0W': 'ZL',
    # },
    # wshq
    'global_future_alias': {
        'NECLA0': 'CL',

        'CMGCA0': 'GC',
        'CMSIA0': 'SI',

        'CEYMA0': 'YM',
        'CEESA0': 'ES',
        'CENQA0': 'NQ',

        'WGCNA0': 'CN',

        # 'LENID3M': 'NID',

        'COZSA0': 'ZS',
        'COZMA0': 'ZM',
        'COZLA0': 'ZL',

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
            'margin_rate': 0.56,
            'order_book_id': 'CL',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 10,
            'exchange': '美国',
            'margin_rate': 0.059,
            'order_book_id': 'GC',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 5000,
            'exchange': '美国',
            'margin_rate': 0.13,
            'order_book_id': 'SI',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 1,
            'exchange': '新加坡',
            'margin_rate': 0.09,
            'order_book_id': 'CN',
            'trading_hours': '7*24',
            'type': 'stock',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 0.5,
            'exchange': '美国',
            'margin_rate': 0.13,
            'order_book_id': 'YM',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 0.5,
            'exchange': '美国',
            'margin_rate': 0.13,
            'order_book_id': 'ES',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 0.5,
            'exchange': '美国',
            'margin_rate': 0.13,
            'order_book_id': 'NQ',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '马来西亚',
        #     'margin_rate': 0.1,
        #     'order_book_id': 'CP',
        #     'trading_hours': '7*24',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 0.1,
        #     'order_book_id': 'NID',
        #     'trading_hours': '7*24',
        #     'type': 'future',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 0.1,
        #     'order_book_id': 'CT',
        #     'trading_hours': '7*24',
        #     'type': 'future',
        #     'feeRate': 0.012
        # },
        {
            'contract_multiplier':50,
            'exchange': '美国',
            'margin_rate': 0.056,
            'order_book_id': 'ZS',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 100,
            'exchange': '美国',
            'margin_rate': 0.07,
            'order_book_id': 'ZM',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        {
            'contract_multiplier': 600,
            'exchange': '美国',
            'margin_rate': 0.06,
            'order_book_id': 'ZL',
            'trading_hours': '7*24',
            'type': 'future',
            'feeRate': 0.012
        },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 1,
        #     'order_book_id': 'AAPL',
        #     'trading_hours': '5*7',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 1,
        #     'order_book_id': 'MSFT',
        #     'trading_hours': '5*7',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 1,
        #     'order_book_id': 'GOOG',
        #     'trading_hours': '5*7',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 1,
        #     'order_book_id': 'FB',
        #     'trading_hours': '5*7',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 1,
        #     'order_book_id': 'AMZN',
        #     'trading_hours': '5*7',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 1,
        #     'order_book_id': 'NFLX',
        #     'trading_hours': '5*7',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 1,
        #     'order_book_id': 'NVDA',
        #     'trading_hours': '5*7',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 1,
        #     'order_book_id': 'AMD',
        #     'trading_hours': '5*7',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # },
        # {
        #     'contract_multiplier': 1,
        #     'exchange': '美国',
        #     'margin_rate': 1,
        #     'order_book_id': 'ROKU',
        #     'trading_hours': '5*7',
        #     'type': 'stock',
        #     'feeRate': 0.012
        # }
    ]
}

cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
