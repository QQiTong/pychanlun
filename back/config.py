import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/shanghai'
    pass

class DevelopmentConfig(Config):
    MONGODB_SETTINGS = {
        'host': '120.77.209.6',
        'port': 27017,
        'db': 'pychanlun',
        'username': 'pychanlun',
        'password': 'chanlun123456'
    }
    pass


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'host': 'mongo-server',
        'port': 27017,
        'db': 'pychanlun',
        'username': 'pychanlun',
        'password': 'chanlun123456'
    }
    pass

config = {
    'default': DevelopmentConfig,
    'production': ProductionConfig
}