import json
from operator import ge
import peewee as pw
from flask import Flask, redirect,\
    render_template, request, jsonify
from orm import Customer, Facture, Pack, PackSubTask, SubTask, Task, db
import os

app = Flask(__name__)


@app.route('/')
def home():
    return redirect('/customers')


@app.route('/customers')
def customers():
    page = int(request.args.get('page', 1))
    emps = Customer.select().where(Customer.regulier == True).paginate(
        page, 7).order_by(Customer.city.asc())
    return render_template('employees.html', customers=emps)


@app.route('/customers_')
def customers_():
    emps = Customer.select().where(Customer.regulier ==
                                   False).order_by(Customer.city.asc())
    return render_template('employees.html', customers=emps, irr=True)


@app.route('/create/customer', methods=['POST'])
def c_customer():
    r = dict(request.form)
    print(r)
    try:
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


@app.route('/facture/customer/<int:pk>')
def f_customer():
    pass


@app.route('/api/customers')
def get_customers():
    return jsonify([{'pk': c.pk, 'name': c.name} for c in Customer.select().order_by(Customer.name.asc())])


@app.route('/tasks')
def tasks():
    tasks = Task.select().order_by(Task.executed_at.desc())
    return render_template('tasks.html', tasks=tasks)


@app.route('/create/task', methods=['POST'])
def c_task():
    r = dict(request.form)
    print(r)
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
            'message': "Tâche bien défacturée"
        })


@app.route('/api/tasks')
def get_tasks():
    return jsonify([{'pk': t.pk, 'name': t.name} for t in Task.select().order_by(Task.executed_at.desc())])


@app.route('/factures')
def factures():
    return render_template('factures.html', factures=Facture.select().order_by(Facture.date.desc()))


@app.route('/create/facture', methods=['POST'])
def c_facture():
    print(request.form.get('customer'))
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
            return jsonify({
                'success': True,
                'message': 'Facture bien supprimée'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Facture déjà envoyé ou toujours associée à des tâches'
            })


@app.route('/view/<hash>')
def view(hash):
    p = os.path.abspath(f'./docs/{hash}.pdf')
    return redirect(f'file://{p}')  # render_template('view.html', hash=hash)


@app.route('/send', methods=['POST'])
def send_facture():
    facture: Facture = Facture.get(
        hash=request.form.get('facture')
    )
    try:
        if not facture.sent:
            facture.send(request.form.get('message').strip())
            facture.regenerate()
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
    return render_template('subtasks.html', subtasks=SubTask.select())


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
    return render_template('packs.html', packs=Pack.select())


@app.route('/create/pack', methods=['POST'])
def c_pack():
    print(request.form)
    pack = json.loads(request.form.get('data'))
    c: Customer = Customer.get(pk=int(pack.get('customer')))
    print(pack)
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


@app.route('/facturer/default', methods=['POST'])
def facture_default():
    _cus = json.loads(request.form.get('customers'))
    try:
        for _cli in _cus:
            pack: Pack = Pack.get(Pack.customer_id == _cli)
            pack.generate_facture(request.form.get('obj'))
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


if __name__ == '__main__':
    app.run(port=5000, debug=True)
