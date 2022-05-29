from datetime import datetime as dt
import os
import peewee as pw
from orm import Customer, Facture, Task
import hashlib as hb
import dateparser as dp

import sys
from jinja2 import Template
import pdfkit


from tabulate import tabulate

from mailer import gmail_authenticate, send_message


def create_facture(client: int, obj: str, tmp: str, fin=None):
    Facture.generate(client, obj, tmp, fin)


def send_facture(facture: str):
    f: Facture = Facture.get(hash=facture)
    f.send()


def create_customer():
    print('='*30+"CRÉATION D'UN CLIENT"+'='*30)
    print('SI VOUS NE CONNAISSEZ PAS UNE VALEUR, TAPEZ ENTRÉE ET CONTINUEZ')
    name = input('Saisissez le nom du client : ')
    porte = int(input("Saissisez le numéro de porte du client : "))
    street = input('Saisissez la rue du client : ')
    city = input("Saisissez la ville du client : ")
    try:
        appart = int(input("Saisissez l'appartement du client : "))
    except ValueError:
        appart = 0
    postal = input("Saisissez le code postal du client : ")
    province = input("Saisissez la province du client : ")
    email = input(
        "Saisissez le mail du client (laissez un vide si non disponible) : ")
    phone = input("Saissisez le téléphone du client : ")
    infos = {
        'name': name,
        'porte': porte,
        'street': street,
        'city': city,
        'appart': appart if appart else None,
        'postal': postal,
        'province': province if province else 'Québec',
        'email': email if email else None,
        'phone': phone if phone else None
    }
    print('='*40)
    # pprint.pprint()
    valid = input(
        f"Voulez-vous créez un client avec ces informations \n {infos} \n ? (O/n) : ")
    if valid == 'O':
        try:
            c = Customer.create(**infos)
        except Exception as e:
            print(e)
        else:
            print(f'Utilisateur {name} créé')
    else:
        print("Création annulée")


def lister_customer():
    print(tabulate([[cus.pk, cus.name, cus.phone]
          for cus in Customer.select()], headers=['ID', 'Nom', 'Contact'], tablefmt='orgtbl'))


def lister_task():
    print(tabulate([[task.pk, task.name, task.customer, 'Oui' if task.facture else 'Non']
          for task in Task.select()], headers=['ID', 'Nom', 'Client', 'Facturé ?'], tablefmt='orgtbl'))


def lister_facture():
    print(tabulate([[fac.hash, fac.customer, fac.date, 'Oui' if fac.sent else 'Non'] for fac in Facture.select()], headers=[
          'Hash', 'Client', 'Date', 'Envoyé ?'], tablefmt='orgtbl'))


def create_task():
    name = input('Quelle tâche avez vous effectuez ? : ')
    price = float(input('Quelle est son coût ? : '))
    _date = dp.parse(
        input('À quelle date avez vous réaliser cette tâche ?: ')
    ).date()
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
    f: Facture = Facture.get(hash=_hash)
    f.delete_()
