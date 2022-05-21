from datetime import datetime as dt
import argparse
from mars import create_customer, create_facture, delete_customer, delete_facture,\
    retrieve_facture, retrieve_factures, send_facture, loadenv
import asyncio

parser = argparse.ArgumentParser()

parser.add_argument(
    'command',
    help="Command to execute",
    choices=['create', 'send', 'delete', 'retrieve']
)

parser.add_argument(
    'option',
    help="Option to command",
    choices=['facture', 'customer', 'factures']
)
parser.add_argument('--customer', '-c', type=int, help="Customer's id")
parser.add_argument(
    '--date',
    '-d',
    help="Date of task execution",
    default=dt.now().date().strftime('%Y-%m-%d')
)
parser.add_argument(
    '--facture',
    '-f',
    help="Facture hash"
)

args = parser.parse_args()

if __name__ == '__main__':
    loadenv()
    if args.command == 'create':
        if args.option == 'facture':
            create_facture(args.customer, args.date)
        elif args.option == 'customer':
            create_customer()
    elif args.command == 'retrieve':
        if args.option == 'facture':
            if retrieve_facture(args.customer, args.date):
                print(retrieve_facture(args.customer, args.date))
        elif args.option == 'factures':
            retrieve_factures(args.date)
    elif args.command == 'send':
        if args.option == 'facture':
            send_facture(args.facture)
    elif args.command == 'delete':
        if args.option == 'customer':
            delete_customer(args.customer)

        if args.option == 'facture':
            delete_facture(args.facture, cus=args.customer, date=args.date)
