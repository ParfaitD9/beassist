import csv
import re
from orm import db, Customer


def load_py(obj: list):
    with db.atomic():
        for nom, addr, phone, region, _, _, mail, _ in obj:
            bloc, city, postal = addr.split(', ')
            porte, rue = bloc.split(maxsplit=1)
            porte = int(porte)
            province = region.split(', ')[-1]

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
                'city': city,
                'postal': postal,
                'province': province,
                'email': _mail,
                'phone': _phone
            }

            c = Customer.create(**infos)

            print(f'{c} created')


if __name__ == '__main__':
    pass
