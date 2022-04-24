import peewee as pw
from datetime import datetime as dt

db = pw.SqliteDatabase('database.db3')

class BaseModel(pw.Model):
    class Meta:
        database = db


class Customer(BaseModel):
    pk = pw.IntegerField(primary_key= True)
    name = pw.CharField()
    adress = pw.CharField()
    phone = pw.CharField()
    city = pw.CharField()
    email = pw.CharField(null= True)

class Facture(BaseModel):
    hash = pw.CharField()
    customer = pw.ForeignKeyField(Customer, backref= 'factures')

class Task(BaseModel):
    pk = pw.CharField(primary_key= True)
    name = pw.CharField()
    price = pw.FloatField()
    taxes = pw.FloatField()
    customer = pw.ForeignKeyField(Customer, backref= 'tasks')
    executed_at = pw.DateField(default= dt.now)

