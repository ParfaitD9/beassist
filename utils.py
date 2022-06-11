import re
from orm import Facture, Task, db, Customer, City
import peewee as pw
from datetime import date as dte
from tabulate import tabulate
import dateparser as dp


def load_client_py(obj: list):
    with db.atomic():
        for nom, addr, phone, region, _, _, mail, _ in obj:
            bloc, city, postal = addr.split(', ')
            porte, rue = bloc.split(maxsplit=1)
            porte = int(porte)
            province = region.split(', ')[-1]
            city, _ = City.get_or_create(name=city)
            r = re.match(
                '^(?P<a>\(\d{3}\)|\d{3})[- ]*(?P<b>\d{3})[- ]*(?P<c>\d{4})', phone
            )

            if r:
                a, b, c = r.group('a'), r.group('b'), r.group('c')
                _phone = f'{a} {b} {c}'
            else:
                _phone = phone.strip()

            if not re.match('^[éèA-z0-9_.-]+@[a-zA-Z0-9.-]+$', mail):
                _mail = None
            else:
                _mail = mail

            infos = {
                'name': nom,
                'porte': porte,
                'street': rue,
                'city': city.pk,
                'postal': postal,
                'province': province,
                'email': _mail,
                'phone': _phone
            }

            c = Customer.create(**infos)

            print(f'{c} created')


def load_task_py(obj):
    with db.atomic():
        for nom, _, _, _, cout, travaux, _, _ in obj:
            try:
                cus = Customer.get(name=nom)
            except (pw.DoesNotExist, ) as e:
                continue
            else:
                t = Task.create(
                    name=travaux[:20],
                    price=float(cout),
                    executed_at=dte.today(),
                    customer=cus
                )

                print(f'Task {nom} created')


def make_point(debut=None, fin=None):
    if debut and fin:
        debut, fin = dp.parse(debut), dp.parse(fin)
        inter = Facture.select().where(debut <= Facture.date <= fin).order_by('date')
    else:
        inter = Facture.select().order_by('date')

    cout = sum(
        [facture.cout for facture in inter]
    )
    nb = inter.count()
    print(
        tabulate([[facture.date, facture.obj, facture.customer, facture.cout]
                  for facture in inter],
                 headers=['Date', 'Objet', 'Client', 'Coût'],
                 tablefmt='orgtbl'
                 )
    )

    return (cout, nb)


if __name__ == '__main__':
    pass
