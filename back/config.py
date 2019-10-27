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
        'url': 'mongodb://root:Chanlun123456@dds-wz973894a77e58141351-pub.mongodb.rds.aliyuncs.com:3717,dds-wz973894a77e58142114-pub.mongodb.rds.aliyuncs.com:3717/pychanlun?authSource=admin&replicaSet=mgset-16710813'
        # 'url': 'mongodb://127.0.0.1:27017/pychanlun'
    }
    pass


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'url': 'mongodb://root:Chanlun123456@dds-wz973894a77e58141351-pub.mongodb.rds.aliyuncs.com:3717,dds-wz973894a77e58142114-pub.mongodb.rds.aliyuncs.com:3717/admin?replicaSet=mgset-16710813'
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
        "SP",
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
        "L"
    ],
    'periodList': [
        '1m',
        '3m',
        '5m',
        '15m',
        '30m',
        '60m',
        '4h',
        '1d',
        '1w'
    ]
}

cfg = config[os.environ.get('PYCHANLUN_CONFIG_ENV', 'default')]