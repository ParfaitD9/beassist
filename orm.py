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

    def __str__(self):
        return f'{self.name} at {self.city}'

    def __repr__(self) -> str:
        return self.__str__()


class Facture(BaseModel):
    hash = pw.CharField(primary_key=True)
    customer = pw.ForeignKeyField(Customer, backref='factures')
    date = pw.DateField(default=dte.today, formats=['%Y-%m-%d'])

    def __str__(self):
        return f'Facture {self.hash} for {self.customer} of {self.date}'

    def __repr__(self) -> str:
        return self.__str__()


class Task(BaseModel):
    pk = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    price = pw.FloatField()
    customer = pw.ForeignKeyField(Customer, backref='tasks')
    executed_at = pw.DateField(default=dte.today)

    def taxes(self):
        return round(self.price*0.14975)

    def __str__(self):
        return f'{self.name} for {self.customer}'

    def __repr__(self) -> str:
        return self.__str__()
