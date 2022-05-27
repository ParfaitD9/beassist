from datetime import datetime as dt
import argparse
import mars
from dotenv import load_dotenv

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    'command',
    choices=['create', 'send', 'delete', 'retrieve', 'lister'],
    help='''
    C'est la commande à executer:
    - create : permet de créer une instance suivant le second arguments (facture, customer ...).
    - send : elle permet d'envoyer une facture. Le seul second argument autorisé actuellement est
        facture. Vous aurez besoins de faire passer l'option (--facture -f)
        avec le hash de la facture pour l'envoyer.
    - delete : elle permet de supprimer un modèle en fonction de son ID, (facture, customer)
        sont acceptés comme second argument actuellement.
    - retrieve : permet de retrouver un modèle grâce à une information, (facture, customer)
        sont acceptés comme second argument actuellement.
    - lister : permet de lister toutes les instances d'un modèle. (task, customer, facture)
        sont acceptés comme second argument actuellement.
'''
)

parser.add_argument(
    'option',
    choices=['facture', 'customer', 'factures', 'task'],
    help='''
    Cet argument est le second, il correspond au modèle sur lequel
        sera opérer l'opération
'''
)
parser.add_argument('--customer', '-c', type=int, help='''
L'id du client pour lequel la tâche sera effectuée.
l'id peut être l'id dans la base données, le nom du client
ou la boîte postale
''')
parser.add_argument(
    '--date',
    '-d',
    default=dt.now().date().strftime('%Y-%m-%d'),
    help='''
La date correspondant à l'execution de la tâche.
Les géneriques comme "aujourd'hui" et "hier" sont acceptés.
Plusieurs formats le sont aussi
'''
)
parser.add_argument(
    '--facture',
    '-f',
    help='''
C'est le hash de la facture sur laquelle vous voulez opérer.
Il est sous le format XXXX-YYYY-(C|I|R)
'''
)

args = parser.parse_args()

if __name__ == '__main__':
    load_dotenv()
    if args.command == 'create':
        if args.option == 'facture':
            mars.create_facture(args.customer, args.date)
        elif args.option == 'customer':
            mars.create_customer()
        elif args.option == 'task':
            mars.create_task()
    elif args.command == 'retrieve':
        if args.option == 'facture':
            if mars.retrieve_facture(args.customer, args.date):
                print(mars.retrieve_facture(args.customer, args.date))
        elif args.option == 'factures':
            mars.retrieve_factures(args.date)
    elif args.command == 'send':
        if args.option == 'facture':
            mars.send_facture(args.facture)
    elif args.command == 'delete':
        if args.option == 'customer':
            mars.delete_customer(args.customer)

        if args.option == 'facture':
            mars.delete_facture(
                args.facture, cus=args.customer, date=args.date)
    elif args.command == 'lister':
        if args.option == 'customer':
            mars.lister_customer()
        elif args.option == 'task':
            mars.lister_task()
        elif args.option == 'facture':
            mars.lister_facture()
