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
        # "AP",
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
