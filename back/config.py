import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    pass


class DevelopmentConfig(Config):
    MONGODB_SETTINGS = {
        'url': 'mongodb://root:Chanlun123456@dds-wz973894a77e58141351-pub.mongodb.rds.aliyuncs.com:3717,dds-wz973894a77e58142114-pub.mongodb.rds.aliyuncs.com:3717/admin?replicaSet=mgset-16710813'
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
    ]
}
