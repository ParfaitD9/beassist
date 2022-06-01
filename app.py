import peewee as pw
from flask import Flask, redirect,\
    render_template, request, jsonify
from orm import Customer, Facture, Task
import os

app = Flask(__name__)


@app.route('/')
def home():
    return redirect('/customers')


@app.route('/customers')
def customers():
    page = int(request.args.get('page', 1))
    emps = Customer.select()
    return render_template('employees.html', customers=emps)


@app.route('/create/customer', methods=['POST'])
def c_customer():
    r = dict(request.form)
    try:
        c = Customer.create(**r)
    except (Exception,) as e:
        return jsonify({
            'success': False,
            'message': e.args[0]
        })
    else:
        return jsonify({
            'success': True,
            'data': {
                'name': c.name,
                'pk': c.pk
            }
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
        c.delete_instance()
        return jsonify({
            'success': True,
            'message': f'Utilisateur {c.name} bien supprimé'
        })


@app.route('/facture/customer/<int:pk>')
def f_customer():
    pass


@app.route('/api/customers')
def get_customers():
    return jsonify([{'pk': c.pk, 'name': c.name} for c in Customer.select()])


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
            'data': {
                'name': t.name,
                'price': t.price,
                'executed_at': t.executed_at,
                'customer_id': t.customer.pk,
            }
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
        }
    else:
        return jsonify({
            'success': True,
            'data': {
                'hash': f.hash,
                'customer': f.customer.pk
            }
        })


@app.route('/delete/facture/<hash>', methods=['POST'])
def d_facture(hash: str):
    try:
        f: Facture = Facture.get(hash=hash.split('-', maxsplit=1)[-1])
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
        else:
            return jsonify({
                'success': False,
                'message': 'Facture déja envoyée'
            })
    except (Exception, ) as e:
        return jsonify({
            'success': False,
            'message': e.args[0]
        })
    else:
        return jsonify({
            'success': True,
            'message': f'Facture {facture.hash} bien envoyée'
        })


@app.route('/subtasks')
def subtask():
    return render_template('subtasks.html')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
