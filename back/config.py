import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/shanghai'
    pass

class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass

config = {
    'default': DevelopmentConfig,
    'production': ProductionConfig
}