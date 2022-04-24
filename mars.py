from datetime import date
from datetime import datetime as dt
from orm import Customer, Task
from jinja2 import Template

import pdfkit

def create_facture(client : Customer, task : Task, tmp : date):
    task = Task.get(Task.customer == client.pk, Task.executed_at == tmp)

    if task:
        with open('templates/facture.html') as f:
            t : Template = Template(f.read())
            now = dt.now().date().strftime('%d/%m/%Y')
            ctx= {
                'task' : task,
                'client' : client,
                'date' : now
            }
            t = t.render(ctx)
            try:
                now = now.replace('/', '-')
                pdfkit.from_string(t, f'./docs/{client.pk}#{now}.pdf')
            except Exception as e:
                print(e)
            else:
                print(f"{task.name}-{client.name}-{now} generated")
    else:
        print("Task not found for this customer and this day.")

if __name__ == '__main__':
    c : Customer = Customer.get(Customer.pk == 1)
    t : Task = Task.get(Task.customer == c.pk)
    d = dt.now().date()

    create_facture(c, t, d)
