from mongoengine import *
import datetime

class Symbol(Document):
    code = StringField()
    name = StringField()
    backend = StringField()