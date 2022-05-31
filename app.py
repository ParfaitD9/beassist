from asyncio import FastChildWatcher
from flask import Flask,\
    render_template, request, jsonify
from orm import Customer, Facture, Task

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/customers')
def customers():
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


@app.route('/api/customers')
def get_customers():
    return jsonify([{'pk': c.pk, 'name': c.name} for c in Customer.select()])


@app.route('/tasks')
def tasks():
    tasks = Task.select().order_by(Task.executed_at.asc())
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


@app.route('/api/tasks')
def get_tasks():
    return jsonify([{'pk': t.pk, 'name': t.name} for t in Task.select().order_by(Task.executed_at.asc())])


@app.route('/factures')
def factures():
    return render_template('factures.html', factures=Facture.select().order_by(Facture.date.asc()))


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


@app.route('/send')
def send_facture():
    facture: Facture = Facture.get(
        hash=request.args.get('facture')
    )
    try:
        facture.send()
    except (Exception, ) as e:
        return jsonify({
            'success': False,
            'message': e.args[0]
        })
    else:
        return jsonify({
            'success': True,
            'data': {
                'hash': facture.hash,
                'customer': facture.customer.email,
            }
        })


if __name__ == '__main__':
    app.run(port=5000, debug=True)
