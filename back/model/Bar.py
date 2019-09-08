from mongoengine import *
import datetime

class Bar(Document):
    time = DateTimeField(required=True, primary_key=True)
    open = DecimalField()
    close = DecimalField()
    high = DecimalField()
    low = DecimalField()
    volume = DecimalField()