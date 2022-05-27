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
    porte = pw.IntegerField()
    street = pw.CharField()
    city = pw.CharField()
    appart = pw.IntegerField(null=True)
    postal = pw.CharField(max_length=12)
    province = pw.CharField(default='Québec')
    email = pw.CharField(null=True)
    phone = pw.CharField(null=True)

    def addresse(self) -> str:
        return (
            f'{self.porte} {self.street} app {self.appart} {self.city}'
            if self.appart else
            f'{self.porte} {self.street} {self.city}'
        )

    def billet(self) -> str:
        return self.addresse() + self.postal

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


class Facture(BaseModel):
    hash = pw.CharField(primary_key=True)
    date = pw.DateField(default=dte.today, formats=['%Y-%m-%d'])
    sent = pw.BooleanField(default=False)
    obj = pw.CharField()
    customer = pw.ForeignKeyField(Customer, backref='factures')

    def __str__(self):
        return f'Facture de {self.customer} pour {self.obj}'

    def __repr__(self) -> str:
        return self.__str__()


class Task(BaseModel):
    pk = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    price = pw.FloatField()
    executed_at = pw.DateField(default=dte.today)
    customer = pw.ForeignKeyField(Customer, backref='tasks')
    facture = pw.ForeignKeyField(
        Facture, backref='tasks', null=True, default=None
    )

    def taxes(self):
        return round(self.price*0.14975)

    def __str__(self):
        return f'{self.name} for {self.customer}'

    def __repr__(self) -> str:
        return self.__str__()
