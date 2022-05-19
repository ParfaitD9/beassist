import peewee as pw
from datetime import datetime as dt
from datetime import date as dte

db = pw.SqliteDatabase('database.db3')


class BaseModel(pw.Model):
    class Meta:
        database = db


class Customer(BaseModel):
    pk = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    adress = pw.CharField()
    phone = pw.CharField()
    city = pw.CharField()
    email = pw.CharField(null=True)


class Facture(BaseModel):
    hash = pw.CharField(primary_key=True)
    customer = pw.ForeignKeyField(Customer, backref='factures')
    date = pw.DateField(default=dte.today, formats=['%Y-%m-%d'])


class Task(BaseModel):
    pk = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    price = pw.FloatField()
    taxes = pw.FloatField()
    customer = pw.ForeignKeyField(Customer, backref='tasks')
    executed_at = pw.DateField(default=dte.today)
