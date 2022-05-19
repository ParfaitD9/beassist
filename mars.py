from datetime import datetime as dt
import os
import smtplib
import ssl
import peewee as pw
from orm import Customer, Facture, Task
import json

from jinja2 import Template
import pdfkit

from email.message import EmailMessage
import pprint


def create_facture(client: int, tmp: str):
    _tmp: dt = dt.strptime(tmp, '%Y-%m-%d').date()
    try:
        client: Customer = Customer.get(Customer.pk == client)
        task: Task = Task.get(Task.customer == client.pk,
                              Task.executed_at == _tmp)
    except Exception as e:
        print("One or multiple args seems invalid")
        return

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
                'date': tmp,
                'facture': f'{client.pk}#{tmp}'
            }
            t = t.render(ctx)
            try:
                f_id = f'{client.pk}#{tmp}'
                pdfkit.from_string(t, f'./docs/{f_id}.pdf')
            except Exception as e:
                print(e.__class__)
            else:
                try:
                    Facture.create(hash=f_id, customer_id=client, date=tmp)
                except (pw.IntegrityError,) as e:
                    print("Same facture seems already exists.")
                else:
                    print(f"Facture {f_id} generated")
    else:
        print("Task not found for this customer and this day.")


def send_facture(facture: str):
    f: Facture = Facture.get(Facture.hash == facture)
    u: Customer = Customer.get(Customer.pk == f.customer)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ctx) as s:
        s.login(
            os.environ.get('EMAIL_USER'),
            os.environ.get('EMAIL_PASSWORD')
        )
        sender = os.environ.get('EMAIL_USER')
        receiver = u.email
        print(f"Successuly connected as {sender}")

        body = '''
        Body of ze email
        '''

        message = EmailMessage()
        message['From'] = sender
        message['To'] = receiver
        message['Subject'] = 'Facture'
        message.set_content(body)

        pdf = f'./docs/{facture}.pdf'
        with open(pdf, 'rb') as b_pdf:
            message.add_attachment(
                b_pdf.read(),
                maintype='application',
                subtype='octet-stream',
                filename=b_pdf.name.removeprefix('./docs/'),
            )
        s.send_message(message)

        print(f'Facture {facture} send to {receiver}.')


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


def delete_customer(key):
    try:
        c: Customer = Customer.get(Customer.pk == key)
    except (pw.DoesNotExist) as e:
        print(f"Aucun utilisateur trouvé pour l'id {key}")
    else:
        c.delete_instance()
        print(f'User {c.name} supprimé.')


def loadenv(path='./.env.json'):
    with open(path) as f:
        d = json.load(f)
        os.environ.update(d)


if __name__ == '__main__':
    c: Customer = Customer.get(Customer.pk == 1)
    d = dt.now().date()

    create_facture(c, d)
