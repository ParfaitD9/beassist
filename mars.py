from datetime import datetime as dt
import os
import peewee as pw
from orm import Customer, Facture, Task
import hashlib as hb
import dateparser as dp

import sys
from jinja2 import Template
import pdfkit


import pprint
from tabulate import tabulate

from mailer import gmail_authenticate, send_message


def create_facture(client: int, tmp: str):
    _tmp: dt = dp.parse(tmp)
    try:
        client: Customer = Customer.get(Customer.pk == client)
        task: Task = Task.get(Task.customer == client.pk,
                              Task.executed_at == _tmp)
    except Exception as e:
        print("One or multiple args seems invalid")
        return
    _hash = hb.blake2b(
        f'{client.pk}#{tmp}'.encode(),
        digest_size=2,
        salt=b'#d$fe2ad'
    ).hexdigest()
    _hash = f'{_hash}-2022-C'

    if task:
        with open('templates/facture.html') as f:
            t: Template = Template(f.read())
            ctx = {
                'task': task,
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
                'date': dt.today().strftime('%Y-%m-%d'),
                'facture': _hash,
                'round': round
            }
            t = t.render(ctx)
            try:
                pdfkit.from_string(t, f'./docs/{_hash}.pdf')
            except Exception as e:
                print(e.__class__)
            else:
                try:
                    Facture.create(
                        hash=_hash, customer_id=client, date=dt.today()
                    )
                except (pw.IntegrityError,) as e:
                    print("Same facture seems already exists.")
                else:
                    print(f"Facture {_hash} generated")
    else:
        print("Task not found for this customer and this day.")


def send_facture(facture: str):
    f: Facture = Facture.get(Facture.hash == facture)
    u: Customer = Customer.get(Customer.pk == f.customer)
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
            [f'./docs/{facture}.pdf']
        )
    except (Exception,) as e:
        print(f'{e} sending mail to {receiver}')
    else:
        print(f'Facture {facture} send to {receiver}. \n Code: \n {r}')


def create_customer():
    print('='*30+"CRÉATION D'UN CLIENT"+'='*30)
    name = input('Saisissez le nom du client : ')
    adress = input("Saissisez l'adresse du client : ")
    phone = input("Saissisez le numéro du client : ")
    city = input("Saisissez la ville du client : ")
    email = input(
        "Saisissez le mail du client (laissez un vide si non disponible) : ")
    print('='*40)
    infos = {
        'nom': name,
        'adresse': adress,
        'Téléphone': phone,
        'Ville': city,
        'Email': email
    }
    pprint.pprint(infos)
    valid = input(
        "Voulez-vous créez un client avec ces informations ? (O/n) : ")
    if valid == 'O':
        try:
            c = Customer.create(
                name=name,
                adress=adress,
                phone=phone,
                city=city,
                email=email if email else None
            )
        except Exception as e:
            print(e)
        else:
            print(f'Utilisateur {name} créé')
    else:
        print("Création annulée")


def lister_customer():
    customers = [customer for customer in Customer.select()]

    print(tabulate([[cus.pk, cus.name, cus.phone]
          for cus in customers], headers=['ID', 'Nom', 'Contact'], tablefmt='orgtbl'))


def create_task():
    name = input('Quelle tâche avez vous effectuez ? : ')
    price = float(input('Quelle est son coût ? : '))
    customer_id = (
        input('À quelle client ? (Vous pouvez saisir le nom où l\'id) : '))
    try:
        if customer_id.isnumeric():
            customer = Customer.get(Customer.pk == customer_id)
        else:
            customer = Customer.get(Customer.name == customer_id)
    except (pw.DoesNotExist, ) as e:
        print('Désolé, ce utilisateur semble ne pas exister')
        sys.exit()

    _date = dp.parse(
        input('À quelle date avez vous réaliser cette tâche ?: ')).date()
    t = {
        'name': name,
        'price': price,
        'customer_id': customer,
        'executed_at': _date
    }
    valid = input(f'Voulez-vous créez la tâche \n {t} ? (O/n) :')
    if valid == 'O':
        t = Task.create(**t)
        print('Tâche créée avec succès')
    else:
        print('Création annulée')


def delete_customer(key):
    try:
        c: Customer = Customer.get(Customer.pk == key)
    except (pw.DoesNotExist) as e:
        print(f"Aucun utilisateur trouvé pour l'id {key}")
    else:
        c.delete_instance()
        print(f'User {c.name} supprimé.')


def retrieve_facture(customer, date) -> Facture:
    _date = dp.parse(date)
    try:
        return Facture.get(customer_id=customer, date=_date)
    except (pw.DoesNotExist, ) as e:
        print('Aucune facture ne correspond à cet utilisateur pour la date saisie')


def retrieve_factures(date):
    _date = dp.parse(date)
    for facture in Facture.select().where(Facture.date == date):
        print(facture)


def delete_facture(_hash=None, cus=None, date=None):
    try:
        f: Facture = Facture.get(
            Facture.hash == _hash or (
                Facture.customer == cus and Facture.date == dp.parse(date))
        )
    except (pw.DoesNotExist,) as e:
        print('Not facture existing with this args')
    else:
        f.delete_instance()
        os.remove(f'./docs/{f.hash}.pdf')
        print('Facture successfully deleted')


if __name__ == '__main__':
    c: Customer = Customer.get(Customer.pk == 1)
    d = dt.now().date()

    create_facture(c, d)
