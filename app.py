import json
import peewee as pw
from flask import Flask, redirect,\
    render_template, request, jsonify, send_from_directory
from orm import City, Customer, Facture, Pack, PackSubTask, SubTask, Task, db
import dateparser as dp
import datetime
import os
import sys
from datetimerange import DateTimeRange
import warnings
import logging


warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)

app = Flask(__name__)


@app.route('/')
def home():
    return redirect('/customers')


@app.route('/api/cities')
def cities():
    return jsonify([
        {'pk': city.pk, 'name': city.name}
        for city in City.select()
    ])


@app.route('/customers')
def customers():
    page = int(request.args.get('page', 1))
    emps = Customer.select().where(
        (Customer.regulier == True) &
        (Customer.prospect == False)
    ).paginate(page, 50).order_by(Customer.city.asc())
    return render_template('_customers.html', customers=emps)


@app.route('/customers_')
def customers_():
    page = int(request.args.get('page', 1))
    emps = Customer.select().where(
        (Customer.regulier == False) &
        (Customer.prospect == False)
    ).paginate(page, 50).order_by(Customer.city.asc())
    return render_template('_customers.html', customers=emps, irr=True)


@app.route('/regularise/customer/<int:pk>', methods=['POST'])
def regulatise_cust(pk):
    try:
        c: Customer = Customer.get(pk=pk)
    except (pw.DoesNotExist, ) as e:
        return jsonify({
            'success': False,
            'message': 'Client non existant'
        })
    else:
        c.regulier = True
        c.save()
        return jsonify({
            'success': True,
            'message': 'Client régularisé :)'
        })


@app.route('/prospects')
def prospects():
    page = int(request.args.get('page', 1))
    pros = Customer.select().where(
        Customer.prospect == True
    ).paginate(page, 50).order_by(Customer.city.asc())
    return render_template('_customers.html', customers=pros, pro=True)


@app.route('/claim/prospect/<int:pk>', methods=['POST'])
def claim(pk):
    try:
        c: Customer = Customer.get(pk=pk)
    except (pw.DoesNotExist, ) as e:
        return jsonify({
            'success': False,
            'message': 'Prospect non existant'
        })
    else:
        c.claim()
        return jsonify({
            'success': True,
            'message': 'Prospect convert :)'
        })


@app.route('/api/prospects')
def get_prospects():
    return jsonify([{'pk': c.pk, 'name': c.name} for c in
                    Customer.select().where(Customer.prospect == True).order_by(Customer.name.asc())])


@app.route('/create/customer', methods=['POST'])
def c_customer():
    r = request.form.to_dict()
    try:
        city, _ = City.get_or_create(name=r.get('city'))
        r.update({
            'city': city.pk
        })
        c = Customer.create(**r) if request.form.get('regulier')\
            else Customer.create(**r, regulier=False)
    except (Exception,) as e:
        return jsonify({
            'success': False,
            'message': f' {e.__class__} : {e.args[0]}'
        })
    else:
        return jsonify({
            'success': True,
            'message': f'Utilisateur {c.name} créé avec succès'
        })


@app.route('/delete/customer/<int:pk>', methods=['POST'])
def d_customer(pk):
    try:
        c: Customer = Customer.get(pk=pk)
    except (pw.DoesNotExist,) as e:
        return jsonify({
            'success': False,
            'message': f'Utilisateur non existant'
        })
    else:
        c.delete_instance(recursive=True)
        return jsonify({
            'success': True,
            'message': f'Utilisateur {c.name} bien supprimé'
        })


@app.route('/api/customers')
def get_customers():
    return jsonify([{'pk': c.pk, 'name': c.name} for c in Customer.select().order_by(Customer.name.asc())])


@app.route('/view/customer/<int:pk>')
def view_customer(pk):
    c: Customer = Customer.get(pk=pk)
    return render_template('view-customer.html', customer=c)
# =================================== BEGIN TASK ==================================


@app.route('/tasks')
def tasks():
    page = int(request.args.get('page', 1))
    tasks = Task.select().paginate(page, 50).order_by(Task.executed_at.desc())
    return render_template('_tasks.html', tasks=tasks)


@app.route('/create/task', methods=['POST'])
def c_task():
    r = request.form.to_dict()
    try:
        t = Task.create(**r)
    except (Exception,) as e:
        return jsonify({
            'success': False,
            'message': e.args[0]
        })
    else:
        return jsonify({
            'success': True,
            'message': f'Tâche {t.name} bien créée pour {t.customer}'
        })


@app.route('/delete/task/<int:pk>', methods=['POST'])
def d_task(pk):
    try:
        t: Task = Task.get(pk=pk)
    except (pw.DoesNotExist, ) as e:
        return jsonify({
            'success': False,
            'message': 'Tâche non existante'
        })
    else:
        if not t.facture:
            t.delete_instance()
            return jsonify({
                'success': True,
                'message': f'Tâche {t.name} bien supprimée'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Tâche déjà facturée'
            })


@app.route('/defacture/task/<int:pk>', methods=['POST'])
def defacture_task(pk):
    try:
        f: Task = Task.get(pk=pk)
    except (pw.DoesNotExist,) as e:
        return jsonify({
            'success': False,
            'message': 'Tâche non existante'
        })
    else:
        f.defacturer()
        return jsonify({
            'success': True,
            'message': "Opération effectuée avec succès"
        })


@app.route('/api/tasks')
def get_tasks():
    return jsonify([{'pk': t.pk, 'name': t.name} for t in Task.select().order_by(Task.executed_at.desc())])


@app.route('/api/tasks/<debut>/<fin>')
def range_tasks(debut, fin):
    return jsonify([
        {
            'date': date.strftime('%Y-%m-%d'),
            'point': Task.select(
                pw.fn.SUM(Task.price)
            ).where(
                Task.executed_at == date
            ).scalar(),
            'count': Task.select().where(
                Task.executed_at == date
            ).count()
        } for date in DateTimeRange(debut, fin).range(datetime.timedelta(days=1))
    ])


@app.route('/factures')
def factures():
    page = int(request.args.get('page', 1))
    return render_template(
        '_factures.html',
        factures=Facture.select().where(Facture.soumission ==
                                        False).paginate(page, 50).order_by(Facture.date.desc())
    )


@app.route('/soumissions')
def soumissions():
    page = int(request.args.get('page', 1))
    return render_template(
        '_factures.html',
        factures=Facture.select().where(Facture.soumission ==
                                        True).paginate(page, 50).order_by(Facture.date.desc()),
        soum=True
    )


@app.route('/create/facture', methods=['POST'])
def c_facture():
    try:
        f = Facture.generate(
            int(request.form.get('customer')),
            request.form.get('obj'),
            request.form.get('start_at'),
            request.form.get('end_at')
        )
        if not f:
            return {
                'success': False,
                'message': 'Facture non générée'
            }
    except (Exception, ) as e:
        print(f'{e} : {e.args[0]}')
        return {
            'success': False,
            'message': f'{e.__class__} : {e.args[0]}'
        }
    else:
        return jsonify({
            'success': True,
            'message': f'Facture {f.hash} générée pour {f.customer}'
        })


@app.route('/delete/facture/<hash>', methods=['POST'])
def d_facture(hash: str):
    try:
        f: Facture = Facture.get(hash=hash)
    except (pw.DoesNotExist,) as e:
        return jsonify({
            'success': False,
            'message': 'Facture non existante'
        })
    else:
        if not f.sent and not f.tasks:
            f.delete_instance()
            f.delete_()
            return jsonify({
                'success': True,
                'message': 'Facture bien supprimée'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Facture déjà envoyé ou toujours associée à des tâches'
            })


@app.route('/facture/mass', methods=['POST'])
def facturaction_mass():
    packs: list[str] = json.loads(request.form.get('packs'))
    for _id in packs:
        pack: Pack = Pack.get(pk=_id)
        try:
            f = pack.generate_facture(request.form.get('msg'))
        except (Exception, ) as e:
            return jsonify({
                'success': False,
                'message': f'{e.__class__} : {e.args[0]} pour le pack {_id}. La facturation s\'est arrêté là'
            })

    return jsonify({
        'success': True,
        'message': 'Tous les packs ont été facturés avec succès'
    })


@app.route('/api/factures/<date>')
def day_factures(date):

    facs: list[Facture] = Facture.select().where(
        (Facture.date == dp.parse(date).date()) &
        (Facture.soumission == False)
    )
    return jsonify({
        'date': date,
        'data': [{
            'hash': fac.hash,
            'sent': fac.sent,
            'cout': float(fac.cout),
            'obj': fac.obj,
            'soumission': fac.soumission,
            'customer': fac.customer.pk
        } for fac in facs]})


@app.route('/api/factures/<debut>/<fin>')
def range_factures(debut, fin):
    return jsonify([
        {
            'date': date.strftime('%Y-%m-%d'),
            'point': Facture.select(
                pw.fn.SUM(Facture.cout)
            ).where(
                (Facture.date == date) &
                (Facture.soumission == False)
            ).scalar(),
            'count': Facture.select().where(
                (Facture.date == date) &
                (Facture.soumission == False)
            ).count()
        } for date in DateTimeRange(debut, fin).range(datetime.timedelta(days=1))
    ])


@app.route('/send', methods=['POST'])
def send_facture():
    facture: Facture = Facture.get(
        hash=request.form.get('facture')
    )
    try:
        if not facture.sent:
            if facture.customer.email:
                facture.send(request.form.get('message').strip())
            else:
                return jsonify({
                    'success': False,
                    'message': 'Courriel non disponible pour le propriétaire de la facture'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Facture déja envoyée'
            })
    except (Exception, ) as e:
        return jsonify({
            'success': False,
            'message': f'{e.__class__} : {e.args[0]}'
        })
    else:
        return jsonify({
            'success': True,
            'message': f'Facture {facture.hash} bien envoyée'
        })


@app.route('/subtasks')
def subtasks():
    page = int(request.args.get('page', 1))
    return render_template('_subtasks.html', subtasks=SubTask.select().paginate(page, 50))


@app.route('/create/subtask', methods=['POST'])
def c_subtask():
    try:
        r = dict(request.form)
        f: SubTask = SubTask.create(**r)
    except (Exception, ) as e:
        return jsonify({
            'success': False,
            'message': f'{e.__class__} : {e.args[0]}'
        })
    else:
        return jsonify({
            'success': True,
            'message': 'Sous tâche créé avec succès'
        })


@app.route('/delete/subtask/<int:pk>', methods=['POST'])
def d_subtask(pk):
    try:
        sb: SubTask = SubTask.get(pk=pk)
    except (pw.DoesNotExist, ) as e:
        return jsonify({
            'success': False,
            'message': 'Sous tâche inexistante'
        })
    else:
        sb.delete_instance()
        return jsonify({
            'success': True,
            'message': 'Sous tâche supprimée avec succès'
        })


@app.route('/api/subtasks')
def get_subtasks():
    return jsonify([{'pk': sub.pk, 'name': sub.name} for sub in SubTask.select()])


@app.route('/packs')
def packs():
    page = int(request.args.get('page', 1))
    return render_template('_packs.html', packs=Pack.select().paginate(page, 50).order_by(Pack.customer.asc()))


@app.route('/create/pack', methods=['POST'])
def c_pack():
    pack = json.loads(request.form.get('data'))
    c: Customer = Customer.get(pk=int(pack.get('customer')))

    with db.atomic():
        try:
            p = Pack.create(
                name=pack.get('name'),
                customer=c
            )
        except (pw.IntegrityError,) as e:
            return jsonify({
                'success': False,
                'message': f'{e.__class__} : {e.args[0]}'
            })
        else:
            for sub in pack.get('subtasks'):
                s, _ = SubTask.get_or_create(
                    name=sub.get('name')
                )
                ps = PackSubTask.create(
                    subtask=s,
                    pack=p,
                    value=sub.get('value')
                )

            return jsonify({
                'success': True,
                'message': 'Pack créé avec succès'
            })


@app.route('/facture/pack/<int:pk>', methods=['POST'])
def f_pack(pk):
    try:
        p: Pack = Pack.get(pk=pk)
    except (pw.DoesNotExist, ) as e:
        return jsonify({
            'success': False,
            'message': 'Pack inexistant'
        })
    else:
        try:
            obj = request.form.get('obj')
            p.generate_facture(obj)
        except (Exception,) as e:
            print(f"Erreur ici {e.__class__} : {e.args[0]}")
            return jsonify({
                'success': False,
                'message': f'{e.__class__} : {e.args[0]}'
            })
        else:
            return jsonify({
                'success': True,
                'message': f'Pack facturé avec objet : {obj}'
            })


@app.route('/delete/pack/<int:pk>', methods=['POST'])
def d_pack(pk):
    try:
        p: Pack = Pack.get(pk=pk)
    except (pw.DoesNotExist, ) as e:
        return jsonify({
            'success': False,
            'message': 'Pack inexistant'
        })
    else:
        try:
            p.delete_instance(recursive=True)
        except (Exception,) as e:
            return jsonify({
                'success': False,
                'message': f'{e.__class__} : {e.args[0]}'
            })
        else:
            return jsonify({
                'success': True,
                'message': f'Pack supprimé'
            })


@app.route('/view/pack/<int:pk>')
def view_pack(pk):
    pack = Pack.get(pk=pk)
    subs = PackSubTask.select().join(Pack).where(Pack.pk == pk)

    return render_template('view-pack.html', pack=pack, subtasks=subs)


@app.route('/facturer/customers', methods=['POST'])
def facturer_customers():
    _cus = json.loads(request.form.get('customers'))
    try:
        for _cli in _cus:
            pack: Pack = Pack.get(Pack.customer_id == _cli)
            pack.generate_facture(request.form.get('obj'))
    except (pw.DoesNotExist, ) as e:
        return jsonify({
            'success': False,
            'message': f'Pack non trouvé pour {Customer.get(pk=_cli)}. La facturation s\'est arrêté à ce niveau.'
        })
    except (Exception, ) as e:
        return jsonify({
            'success': False,
            'message': f'{e.__class__} : {e.args[0]}'
        })
    else:
        return jsonify({
            'success': True,
            'message': 'Clients facturés'
        })


@app.route('/send/tomass', methods=['POST'])
def send_tomass():
    msg = request.form.get('message').strip()
    _factures = json.loads(request.form.get('factures'))

    try:
        for facture in _factures:
            f: Facture = Facture.get(hash=facture)
            if not f.sent:
                f.send(msg)
                f.regenerate()
    except (Exception, ) as e:
        return jsonify({
            'success': False,
            'message': f'{e.__class__} : {e.args[0]}'
        })
    else:
        return jsonify({
            'success': True,
            'message': 'Factures envoyé'
        })


@app.route('/make/point')
def make_point():
    today = datetime.datetime.now().date()
    month = datetime.datetime(today.year, today.month, 1)
    cash = Facture.select(pw.fn.SUM(Facture.cout)).where(
        month <= Facture.date <= today).scalar() or 0
    casks = Task.select().where(month <= Task.executed_at <= today).count()
    cust = Customer.select().where(month <= Customer.joined <= today).count()
    return render_template('point.html', cash=cash, casks=casks, custs=cust)


@app.route('/view/<hash>')
def view_pdf(hash):
    return send_from_directory(os.getenv('DOCS_PATH'), f'{hash}.pdf')


if __name__ == '__main__':
    app.run(debug=True)
