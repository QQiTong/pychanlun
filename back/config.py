import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/shanghai'
    pass


class DevelopmentConfig(Config):
    MONGODB_SETTINGS = {
        'host': '127.0.0.1',
        'port': 27017,
        'db': 'pychanlun',
    }
    pass


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'host': 'localhost',
        'port': 27017,
        'db': 'pychanlun',
        'username': '',
        'password': ''
    }
    pass


config = {
    'default': DevelopmentConfig,
    'production': ProductionConfig
}
