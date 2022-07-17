import csv
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
import time
from dotenv import load_dotenv
import logging

load_dotenv()

DOCS_PATH = os.getenv('DOCS_PATH')
COMPTA_PATH = os.getenv('COMPTA_PATH')
BACKUP_PATH = os.getenv('BACKUP_PATH')
CSV_PATH = os.getenv('CSV_PATH')


db = pw.SqliteDatabase('database.db3')


class BaseModel(pw.Model):
    class Meta:
        database = db


class City(BaseModel):
    pk = pw.IntegerField(primary_key=True)
    name = pw.CharField()

    def serialize(self):
        return {
            'pk': self.pk,
            'name': self.name
        }

    @staticmethod
    def load_from_csv(filename='./csv/cities.csv'):
        City.delete().execute()
        with open(filename, encoding='utf-8') as f:
            r = csv.reader(f)
            with db.atomic():
                for (city,) in list(r)[1:]:
                    c, _ = City.get_or_create(name=city)
                    print(f'Ville {c.name} créé !')

    @staticmethod
    def dump_to_csv(filename='./csv/cities.csv'):
        with open(filename, 'w') as f:
            w = csv.writer(f)
            w.writerow(['name', ])
            with db.atomic():
                w.writerows([[city.name, ] for city in City.select()])

    def __str__(self):
        return f'Ville : {self.name}'

    def __repr__(self) -> str:
        return self.__str__()


class Customer(BaseModel):
    pk = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    porte = pw.IntegerField()
    street = pw.CharField()
    city: City = pw.ForeignKeyField(City, backref='customers')
    appart = pw.IntegerField(null=True)
    joined = pw.DateField(default=dt.today)
    postal = pw.CharField(max_length=12)
    province = pw.CharField(default='Québec')
    email = pw.CharField(null=True)
    phone = pw.CharField(null=True)
    statut = pw.CharField(
        max_length=1,
        choices=('I', 'C', 'R'),
        default='C'
    )
    regulier = pw.BooleanField(default=True)
    prospect = pw.BooleanField(default=False)

    @staticmethod
    def lister():
        print(tabulate([[cus.pk, cus.name, cus.phone]
                        for cus in Customer.select()], headers=['ID', 'Nom', 'Contact'], tablefmt='orgtbl'))

    def addresse(self) -> str:
        return (
            f'{self.porte} {self.street} app {self.appart} {self.city.name}'
            if self.appart else
            f'{self.porte} {self.street} {self.city.name}'
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

    def serialize(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'porte': self.porte,
            'street': self.street,
            'city': self.city.serialize(),
            'appart': self.appart,
            'joined': self.joined,
            'postal': self.postal,
            'province': self.province,
            'email': self.email,
            'phone': self.phone,
            'statut': self.statut,
            'regulier': self.regulier,
            'prospect': self.prospect
        }

    def claim(self):
        self.prospect = False
        self.save()

    @staticmethod
    def load_from_csv(filename='./csv/customers.csv'):
        Customer.delete().execute()
        with open(filename, encoding='utf-8') as f:
            reader = csv.reader(f)
            with db.atomic():
                for nom, porte, street, city, appart, joined, postal, prov, mail, ph, stt, reg, pp in list(reader)[1:]:
                    city, _ = City.get_or_create(pk=int(city))
                    city: City
                    infos = {
                        'name': nom,
                        'porte': int(porte),
                        'street': street,
                        'city': city.pk,
                        'appart': appart if appart else None,
                        'joined': joined if joined else dt.today(),
                        'postal': postal,
                        'province': prov,
                        'email': mail if mail else None,
                        'phone': ph if ph else None,
                        'statut': stt,
                        'regulier': bool(int(reg)),
                        'prospect': bool(int(pp))
                    }
                    c: Customer = Customer.create(**infos)
                    print(f'Client {c.name} créé')

    @staticmethod
    def backup(filename='./backup/customers.csv'):
        fields = ['pk', 'name', 'porte', 'street', 'city', 'appart', 'joined',
                  'postal', 'province', 'email', 'phone', 'statut', 'regulier', 'prospect']

        with open(filename, 'w') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for cus in Customer.select():
                cus: Customer
                _cus = cus.serialize()
                _cus.update({'city': cus.city.name})
                w.writerow(_cus)

    @staticmethod
    def load_backup(filename='./backup/customers.csv'):
        if os.path.exists(filename):
            Customer.delete().execute()
            with open(filename, 'r') as f:
                r = csv.DictReader(f)
                with db.atomic():
                    for cus in r:
                        Customer.create(**Customer.clean(cus))
        else:
            print(f"{filename} inexistant. Backup Customer annulé")

    @staticmethod
    def clean(read: dict):
        r = {
            'name': read.get('name'),
            'porte': int(read.get('porte')),
            'street': read.get('street'),
            'city': read.get('city'),
            'appart': read.get('appart') if read.get('appart') else None,
            'joined': read.get('joined') if read.get('joined') else dt.today(),
            'postal': read.get('postal'),
            'province': read.get('province'),
            'email': read.get('email') if read.get('email') else None,
            'phone': read.get('phone') if read.get('phone') else None,
            'statut': read.get('statut'),
            'regulier': True if read.get('regulier') == "True" else False,
            'prospect': True if read.get('prospect') == "True" else False
        }

        return r

    def __str__(self):
        return f'Client : {self.name}'

    def __repr__(self) -> str:
        return self.__str__()


class Facture(BaseModel):
    hash = pw.CharField(primary_key=True)
    date = pw.DateField(default=dt.today, formats=['%Y-%m-%d'])
    sent = pw.BooleanField(default=False)
    cout = pw.DecimalField()
    obj = pw.CharField()
    soumission = pw.BooleanField(default=False)
    customer: Customer = pw.ForeignKeyField(Customer, backref='factures')

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
                print(
                    f'Génération de facture pour les tâches du {_tmp} au {_fin}')

            else:
                print(
                    f'Génération de facture pour les tâches du {_tmp}')
                exp = ((Task.executed_at == _tmp)
                       & (Task.customer == client)
                       & (Task.facture == None))

            tasks = Task.select().where(exp).order_by(Task.executed_at.asc())
        except Exception as e:
            print("One or multiple args seems invalid")
            return
        _hash = hb.blake2b(
            (f'{client.pk}#{tmp}:{fin}' if fin else f'{client.pk}#{tmp}').encode(),
            digest_size=4,
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
                    pdfkit.from_string(t, os.path.join(
                        DOCS_PATH, f'{_hash}.pdf')
                    )
                except Exception as e:
                    print(e.__class__, e.args[0])
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
            print(
                "Pas de tâches non facturés trouvées pour cette date ou cet intervalle")

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
            print(f'Affichage des factures du {debut} au {fin}')
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

    @staticmethod
    def clean(read: dict):
        return {
            'hash': read.get('hash'),
            'date': read.get('date'),
            'sent': True if read.get('sent') == "True" else False,
            'cout': float(read.get('cout')),
            'obj': read.get('obj'),
            'soumission': True if read.get('soumission') == "True" else False,
            'customer': int(read.get('customer'))
        }

    @staticmethod
    def backup(filename='./backup/factures.csv'):
        fields = ['hash', 'date', 'sent', 'cout',
                  'obj', 'soumission', 'customer']
        with open(filename, 'w') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            for fac in Facture.select():
                fac: Facture
                _fac = fac.serialize()
                _fac.update({'customer': fac.customer.pk})
                w.writerow(_fac)

    @staticmethod
    def load_backup(filename='./backup/factures.csv'):
        fields = ['hash', 'date', 'sent', 'cout',
                  'obj', 'soumission', 'customer']
        if os.path.exists(filename):
            Facture.delete().execute()
            with db.atomic():
                with open(filename) as f:
                    r = csv.DictReader(f, fieldnames=fields)
                    for fac in r:
                        Facture.create(**Facture.clean(fac))
        else:
            print(f"{filename} inexistant. Backup Facture annulé")

    def serialize(self):
        return {
            'hash': self.hash,
            'date': self.date,
            'sent': self.sent,
            'cout': self.cout,
            'obj': self.obj,
            'soumission': self.soumission,
            'customer': self.customer.serialize()
        }

    def regenerate(self):
        src = os.path.join(DOCS_PATH, f'{self.hash}.pdf')
        dest = os.path.join(
            COMPTA_PATH, f'{self.customer.statut}/{self.customer.name}')
        os.makedirs(dest, exist_ok=True)
        shutil.copy(src, dest)

    def send(self, corps):
        if not self.sent:
            u: Customer = Customer.get(Customer.pk == self.customer)
            receiver = u.email
            srv = gmail_authenticate()
            body = corps
            try:
                r = send_message(
                    srv,
                    receiver,
                    'Facture de la part de Excellence Entretien',
                    body,
                    [f'./docs/{self.hash}.pdf']
                )
            except (Exception,) as e:
                print(
                    f'{e.__class__} {e.args[0]} in sending mail to {receiver}')
            else:
                self.sent = True
                self.save()
                if not self.soumission:
                    self.regenerate()
                print(
                    f'Facture {self.hash} send to {receiver}.')

                return True
        else:
            return False

    def delete_(self):
        try:
            os.remove(
                os.path.join(DOCS_PATH, f'{self.hash}.pdf')
            )
        except (FileNotFoundError, ) as e:
            pass
        except (Exception,) as e:
            print(f'{e.__class__} : {e.args[0]}')
        finally:
            print(f'Facture {self.hash} successfully deleted')

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
    customer: Customer = pw.ForeignKeyField(Customer, backref='tasks')
    facture: Facture = pw.ForeignKeyField(
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

    @staticmethod
    def clean(read: dict):
        return {
            'pk': int(read.get('pk')),
            'name': read.get('name'),
            'price': float(read.get('price')),
            'executed_at': read.get('executed_at'),
            'customer': int(read.get('customer')),
            'facture': read.get('facture'),
        }

    @staticmethod
    def backup(filename='./backup/tasks.csv'):
        fields = ['pk', 'name', 'price', 'executed_at', 'customer', 'facture']
        with open(filename, 'w') as f:
            w = csv.DictWriter(f, fields)
            for task in Task.select():
                task: Task
                _task = task.serialize()
                _task.update({
                    'customer': task.customer.pk,
                    'facture': task.facture.hash if task.facture else None
                })
                w.writerow(_task)

    @staticmethod
    def load_backup(filename='./backup/tasks.csv'):
        fields = ['pk', 'name', 'price', 'executed_at', 'customer', 'facture']
        if os.path.exists(filename):
            Task.delete().execute()
            with open(filename) as f:
                r = csv.DictReader(f, fields)
                with db.atomic():
                    for task in r:
                        Task.create(**Task.clean(task))
        else:
            print(f"{filename} inexistant. Backup Customer annulé")

    def serialize(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'price': self.price,
            'executed_at': self.executed_at,
            'customer': self.customer.serialize(),
            'facture': self.facture.serialize()
        }

    def defacturer(self):
        self.facture = None
        self.save()

    def __str__(self):
        return f'{self.name} for {self.customer}'

    def __repr__(self) -> str:
        return self.__str__()


class SubTask(BaseModel):
    pk = pw.IntegerField(primary_key=True)
    name = pw.CharField()

    @staticmethod
    def backup(filename='./backup/subtasks.csv'):
        with open(filename, 'w') as f:
            w = csv.DictWriter(f, ['pk', 'name'])
            for sub in SubTask.select():
                sub: SubTask
                _sub = sub.serialize()
                w.writerow(_sub)

    @staticmethod
    def load_backup(filename='./backup/subtasks.csv'):
        if os.path.exists(filename):
            SubTask.delete().execute()
            with open(filename) as f:
                w = csv.DictReader(f, ['pk', 'name'])
                for sub in w:
                    SubTask.create(**SubTask.clean(sub))
        else:
            print(f"{filename} inexistant. Backup Customer annulé")

    @staticmethod
    def clean(read: dict):
        return {
            'pk': int(read.get('pk')),
            'name': read.get('name'),
        }

    def serialize(self):
        return {
            'pk': self.pk,
            'name': self.name
        }

    def __str__(self):
        return self.name


class Pack(BaseModel):
    pk = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    customer: Customer = pw.ForeignKeyField(
        Customer, unique=True, backref='pack')

    @staticmethod
    def backup(filename='./backup/packs.csv'):
        with open(filename, 'w') as f:
            w = csv.DictWriter(f, fieldnames=['pk', 'name', 'customer'])
            for pack in Pack.select():
                pack: Pack
                _pack = pack.serialize()
                _pack.update({
                    'customer': pack.customer.pk
                })
                w.writerow(_pack)

    @staticmethod
    def load_backup(filename='./backup/packs.csv'):
        if os.path.exists(filename):
            Pack.delete().execute()
            with db.atomic():
                with open(filename) as f:
                    r = csv.DictReader(
                        f, fieldnames=['pk', 'name', 'customer'])
                    for pack in r:
                        Pack.create(**Pack.clean(pack))
        else:
            print(f'{filename} not found')

    @staticmethod
    def clean(read: dict):
        return {
            'pk': int(read.get('pk')),
            'name': read.get('name'),
            'customer': int(read.get('customer')),
        }

    def generate_facture(self, obj) -> Facture:
        _hash = hb.blake2b(
            f'{self.name}:{obj}:{int(time.time())}'.encode(),
            digest_size=4,
            salt=os.getenv('HASH_SALT').encode()
        ).hexdigest()
        _hash = f'{_hash}-{dt.today().year}-{self.customer.statut}'
        tasks = PackSubTask.select().join(Pack).where(Pack.customer == self.customer)
        client: Customer = self.customer
        today = dt.today().strftime('%Y-%m-%d')
        print(f"Génération at {today}")
        with open('templates/pack.html' if not self.customer.prospect else 'templates/soumission.html') as f:
            t: Template = Template(f.read())
            ctx = {
                'tasks': tasks,
                'client': client,
                'admin': Customer(
                    name=os.getenv('ADMIN_FULLNAME'),
                    adress=os.getenv('ADIMN_ADRESS'),
                    phone=os.getenv('ADMIN_PHONE'),
                    city=os.getenv('ADMIN_CITY'),
                    email=os.getenv('EMAIL_USER')
                ),
                'nas': os.getenv('ADMIN_NAS'),
                'tvs': os.getenv('ADMIN_TVS'),
                'date': today,
                'facture': _hash,
                'obj': obj,
                'ht': self.price(),
                'taxes': round(self.price()*0.14975, 2)
            }
            t = t.render(ctx)

            try:
                pdfkit.from_string(t, os.path.join(DOCS_PATH, f'{_hash}.pdf'))
            except Exception as e:
                print(e.__class__, e.args[0])
            else:
                try:
                    f = Facture.create(
                        hash=_hash,
                        customer_id=client.pk,
                        date=today,
                        cout=self.price(),
                        obj=obj,
                        soumission=True if client.prospect else False
                    )
                except (pw.IntegrityError,) as e:
                    print("Same facture seems already exists.")
                else:
                    print(f"Facture {_hash} generated")
                    if not f.soumission:
                        t = Task.create(
                            name=f.obj,
                            price=f.cout,
                            executed_at=f.date,
                            customer=f.customer,
                            facture=f
                        )
                    return f

    def price(self):
        return float(sum([psub.value for psub
                          in PackSubTask.select().join(Pack).where(Pack.customer == self.customer)]))

    def serialize(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'customer': self.customer.serialize()
        }

    def __str__(self):
        return self.name


class PackSubTask(BaseModel):
    value = pw.DecimalField(default=0.00, null=True)
    subtask: SubTask = pw.ForeignKeyField(SubTask)
    pack: Pack = pw.ForeignKeyField(Pack, on_delete='CASCADE')

    @staticmethod
    def load_from_csv(filename='./csv/packs.csv'):
        PackSubTask.delete().execute()
        with db.atomic():
            with open(filename, encoding='utf-8') as f:
                r = csv.reader(f)
                for cus, task, price in r:
                    c: Customer = Customer.get(name=cus)
                    st, _ = SubTask.get_or_create(name=task)
                    pack, _ = Pack.get_or_create(
                        customer=c,
                        name=f'Pack : {c.name}'
                    )

                    psk = PackSubTask.create(
                        subtask=st,
                        pack=pack,
                        value=float(price.replace(',', '.'))
                    )

    @staticmethod
    def backup(filename='./backup/packsubtasks.csv'):
        if os.path.exists(filename):
            with open(filename, 'w') as f:
                w = csv.DictWriter(f, fieldnames=[
                    'value', 'subtask', 'pack'])
                for pks in PackSubTask.select():
                    pks: PackSubTask
                    w.writerow(
                        {'value': pks.value, 'subtask': pks.subtask, 'pack': pks.pack}
                    )

    @staticmethod
    def load_backup(filename='./backup/packs.csv'):
        if os.path.exists(filename):
            PackSubTask.delete().execute()
            with open(filename) as f:
                r = csv.DictReader(f, fieldnames=[
                    'value', 'subtask', 'pack'])
                for pks in r:
                    pks: dict
                    PackSubTask.create({
                        'value': pks.get('value'),
                        'subtask': int(pks.get('subtask')),
                        'pack': int(pks.get('pack'))
                    })
        else:
            print(f"{filename} inexistant. Backup PackSubtasks annulé")
