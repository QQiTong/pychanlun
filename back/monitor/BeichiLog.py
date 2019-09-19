from mongoengine import *
import datetime

class BeichiLog(Document):
    date_created = StringField(required=True, default = datetime.datetime.now().strftime("%m-%d %H:%M"))
    symbol = StringField()
    period = StringField()
    price = DecimalField()
    signal = BooleanField()
    remark = StringField()