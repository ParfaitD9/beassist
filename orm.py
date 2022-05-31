import shutil
import peewee as pw
from mailer import gmail_authenticate, send_message
from datetime import date as dt
import os
import dateparser as dp
import pdfkit
import hashlib as hb
from jinja2 import Template
from tabulate import tabulate

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
    statut = pw.CharField(
        max_length=1,
        choices=('I', 'C', 'R'),
        default='C'
    )

    @staticmethod
    def lister():
        print(tabulate([[cus.pk, cus.name, cus.phone]
                        for cus in Customer.select()], headers=['ID', 'Nom', 'Contact'], tablefmt='orgtbl'))

    def addresse(self) -> str:
        return (
            f'{self.porte} {self.street} app {self.appart} {self.city}'
            if self.appart else
            f'{self.porte} {self.street} {self.city}'
        )

    def billet(self) -> str:
        return self.addresse() + self.postal

    def facture_him(self, obj: str):
        tasks = Task.select().where(
            (Task.customer == self) &
            (Task.facture == None)
        ).order_by('-date')

        Facture.generate(
            self.pk,
            obj,
            '2022-01-01',
            dt.today().strftime('%Y-%m-%d')
        )

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


class Facture(BaseModel):
    hash = pw.CharField(primary_key=True)
    date = pw.DateField(default=dt.today, formats=['%Y-%m-%d'])
    sent = pw.BooleanField(default=False)
    cout = pw.DecimalField()
    obj = pw.CharField()
    customer = pw.ForeignKeyField(Customer, backref='factures')

    @staticmethod
    def generate(client: int, obj: str, tmp: str, fin=None):
        '''
        Permet de générer une facture
        Args:
            client :int: l'ID du client auquel est destiné la facture\n
            obj :str: L'objet de la facture à insérer dans le titre\n
            tmp :str: Date des travaux associé à la facture (ou début de l'intervalle)\n
            fin :str: fin de l'intervalle

            Le format idéal de la date est YYYY-MM-DD
        '''
        _tmp: dt = dp.parse(tmp).date()
        today = dt.today().strftime('%Y-%m-%d')

        if fin:
            _fin: dt = dp.parse(fin).date()
        try:
            client: Customer = Customer.get(Customer.pk == client)
            if fin:
                exp = ((_tmp <= Task.executed_at <= _fin)
                       & (Task.customer == client)
                       & (Task.facture == None))
                print(f'Tâches du {_tmp} au {_fin}')

            else:
                print(f'Tâches du {_tmp}')
                exp = ((Task.executed_at == _tmp)
                       & (Task.customer == client)
                       & (Task.facture == None))

            tasks = Task.select().where(exp)
        except Exception as e:
            print("One or multiple args seems invalid")
            return
        _hash = hb.blake2b(
            (f'{client.pk}#{tmp}:{fin}' if fin else f'{client.pk}#{tmp}').encode(),
            digest_size=2,
            salt=b'#d$fe2ad'
        ).hexdigest()
        _hash = f'{_hash}-2022-C'

        if tasks:
            with open('templates/facture.html') as f:
                t: Template = Template(f.read())
                ctx = {
                    'tasks': tasks,
                    'client': client,
                    'admin': Customer(
                        name=os.environ.get('ADMIN_FULLNAME'),
                        adress=os.environ.get('ADIMN_ADRESS'),
                        phone=os.environ.get('ADMIN_PHONE'),
                        city=os.environ.get('ADMIN_CITY'),
                        email=os.environ.get('EMAIL_USER')
                    ),
                    'nas': os.environ.get('ADMIN_NAS'),
                    'tvs': os.environ.get('ADMIN_TVS'),
                    'date': today,
                    'facture': _hash,
                    'obj': obj,
                    'ht': sum([task.price for task in tasks]),
                    'taxes': round(sum([task.price for task in tasks])*0.14975, 2)
                }
                t = t.render(ctx)
                cout = sum([task.price for task in tasks])
                try:
                    pdfkit.from_string(t, f'./docs/{_hash}.pdf')
                except Exception as e:
                    print(e.__class__)
                else:
                    try:
                        f = Facture.create(
                            hash=_hash,
                            customer_id=client.pk,
                            date=today,
                            cout=cout,
                            obj=obj
                        )
                    except (pw.IntegrityError,) as e:
                        print("Same facture seems already exists.")
                    else:
                        query = Task.update(facture=f).where(exp)
                        query.execute()
                        print(f"Facture {_hash} generated")

                        return f
        else:
            print("Pas de tâches non facturés trouvées pour cette date ou cet intervalle")

    @staticmethod
    def lister(debut=None, fin=None):
        '''
        Lister les factures générées dans un intervalle
        debut:str: Date de début pour les factures
        fin:str: Date de fin pour les factures

        Le format idéal YYYY-MM-DD
        '''

        if debut and fin:
            debut, fin = dp.parse(debut), dp.parse(fin)
            print(f'Factures du {debut} au {fin}')
            facs = [[fac.hash, fac.customer, fac.date, 'Oui' if fac.sent else 'Non']
                    for fac in Facture.select().where(debut <= Facture.date <= fin)]
        else:
            facs = [[fac.hash, fac.customer, fac.date,
                     'Oui' if fac.sent else 'Non'] for fac in Facture.select()]
        print(tabulate(facs, headers=[
            'Hash', 'Client', 'Date', 'Envoyé ?'], tablefmt='orgtbl'))

    @staticmethod
    def sendall(debut=None, fin=None):
        if debut and fin:
            debut = dp.parse(debut)
            fin = dp.parse(fin)
            inter = Facture.select().where(
                (Facture.sent == False) &
                (debut <= Facture.date <= fin)
            ).order_by('-date')
        else:
            inter = Facture.select().where(Facture.sent == False).order_by('-date')

        for facture in inter:
            facture: Facture
            facture.send()

    def regenerate(self):
        _hash = self.hash.split('-')[0]
        shutil.copyfile(f'./docs/{self.hash}.pdf',
                        f'./compta/{self.customer.name}-{_hash}.pdf')

    def send(self):
        u: Customer = Customer.get(Customer.pk == self.customer)
        receiver = u.email
        srv = gmail_authenticate()
        body = '''
    Bonjour cher client,
Vous trouverez ci-joint la facturation des travaux effectués sur votre terrain entre
le 15 et le 28 Avril 2022.

Si vous voyez des erreurs, s'il vous plaît communiquer avec moi.

Bien à vous
Marc-Antoine Cloutier
Entretien Excellence & Cie
            
Lavage de vitres - Solutions durables et R&D
514 268 4393
    '''
        try:
            r = send_message(
                srv,
                receiver,
                'Facture de la part de Excellence Entretien',
                body,
                [f'./docs/{self.hash}.pdf']
            )
        except (Exception,) as e:
            print(f'{e} sending mail to {receiver}')
        else:
            self.sent = True
            self.save()
            print(f'Facture {self.hash} send to {receiver}. \n Code: \n {r}')

    def delete_(self):
        self.delete_instance()
        os.remove(f'./docs/{self.hash}.pdf')
        print('Facture successfully deleted')

    def ht(self):
        return sum((task.price for task in self.tasks))

    def ttc(self):
        return round(self.ht() * 1.14975, 2)

    def __str__(self):
        return f'Facture de {self.customer} pour {self.obj}'

    def __repr__(self) -> str:
        return self.__str__()


class Task(BaseModel):
    pk = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    price = pw.FloatField()
    executed_at = pw.DateField(default=dt.today)
    customer = pw.ForeignKeyField(Customer, backref='tasks')
    facture = pw.ForeignKeyField(
        Facture, backref='tasks', null=True, default=None
    )

    @staticmethod
    def lister(debut=None, fin=None):
        if debut and fin:
            debut, fin = dp.parse(debut), dp.parse(fin)
            _tasks = [[task.pk, task.name, task.customer, task.executed_at, 'Oui' if task.facture else 'Non']
                      for task in Task.select().where(debut <= Task.executed_at <= fin)]
        else:
            _tasks = [[task.pk, task.name, task.customer, task.executed_at, 'Oui' if task.facture else 'Non']
                      for task in Task.select()]
        print(tabulate(_tasks, headers=[
              'ID', 'Nom', 'Client', 'Date', 'Facturé ?'], tablefmt='orgtbl'))

    def defacturer(self):
        self.facture = None
        self.save()

    def __str__(self):
        return f'{self.name} for {self.customer}'

    def __repr__(self) -> str:
        return self.__str__()
