from mongoengine import *
import datetime

class Strategy3Log(Document):
    date_created = DateTimeField(required=True, default = datetime.datetime.utcnow)
    symbol = StringField()
    period = StringField()
    raw_data = DictField()
    signal = BooleanField()
    remark = StringField()