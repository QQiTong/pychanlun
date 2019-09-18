from mongoengine import *
import datetime

class BeichiLog(Document):
    date_created = DateTimeField(required=True, default = datetime.datetime.utcnow)
    symbol = StringField()
    period = StringField()
    price = DecimalField()
    signal = BooleanField()
    remark = StringField()