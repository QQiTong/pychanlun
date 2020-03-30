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
        "RB",
        "HC",
        "RU",
        "NI",
        "FU",
        "ZN",
        # "SP",
        "BU",
        "AU",
        "AG",
        "MA",
        "TA",
        "SR",
        "OI",
        "AP",
        "CF",
        "M",
        "I",
        "EG",
        "J",
        "JM",
        "PP",
        # "L",
        "P",
        "RM",
        "Y"
    ],
    # 商品期货保证金率一般固定，只有过节会变下。因为换合约期间需要拿到老合约保证金率，因此保存起来
    'futureConfig': {
        'RB': {'margin_rate': 0.09, 'contract_multiplier': 10},
        'HC': {'margin_rate': 0.09, 'contract_multiplier': 10},
        'RU': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'FU': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'BU': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'AU': {'margin_rate': 0.08, 'contract_multiplier': 1000},
        'AG': {'margin_rate': 0.12, 'contract_multiplier': 15},
        'ZN': {'margin_rate': 0.1, 'contract_multiplier': 5},
        'NI': {'margin_rate': 0.1, 'contract_multiplier': 1},
        'MA': {'margin_rate': 0.07, 'contract_multiplier': 10},
        'TA': {'margin_rate': 0.06, 'contract_multiplier': 5},
        'SR': {'margin_rate': 0.05, 'contract_multiplier': 10},
        'OI': {'margin_rate': 0.05, 'contract_multiplier': 10},
        'CF': {'margin_rate': 0.07, 'contract_multiplier': 5},
        'M': {'margin_rate': 0.06, 'contract_multiplier': 10},
        'I': {'margin_rate': 0.08, 'contract_multiplier': 100},
        'EG': {'margin_rate': 0.11, 'contract_multiplier': 10},
        'J': {'margin_rate': 0.08, 'contract_multiplier': 100},
        'JM': {'margin_rate': 0.08, 'contract_multiplier': 60},
        'PP': {'margin_rate': 0.07, 'contract_multiplier': 5},
        'P': {'margin_rate': 0.07, 'contract_multiplier': 10},
        'RM': {'margin_rate': 0.06, 'contract_multiplier': 10},
        'Y': {'margin_rate': 0.06, 'contract_multiplier': 10},
        'BTC': {'margin_rate': 0.05, 'contract_multiplier': 1},
        'CL': {'margin_rate': 1, 'contract_multiplier': 1},
        'GC': {'margin_rate': 1, 'contract_multiplier': 1},
        'SI': {'margin_rate': 1, 'contract_multiplier': 1},
        'CT': {'margin_rate': 1, 'contract_multiplier': 1},
        'S': {'margin_rate': 1, 'contract_multiplier': 1},
        'SM': {'margin_rate': 1, 'contract_multiplier': 1},
        'BO': {'margin_rate': 1, 'contract_multiplier': 1},
        'NID': {'margin_rate': 1, 'contract_multiplier': 1},
        'ZSD': {'margin_rate': 1, 'contract_multiplier': 1}
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
    # CL:原油; GC:黄金;SI:白银; CT:棉花;S:大豆;SM:豆粕; BO:豆油;NID:伦镍; ZSD:伦锌;
    'globalFutureSymbol': ['CL', 'GC', 'SI', 'CT', 'S', 'SM', 'BO', 'NID', 'ZSD']
}

cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]
