from datetime import datetime as dt
import argparse
from mars import create_facture, send_facture

parser = argparse.ArgumentParser()

parser.add_argument(
    'command',
    help= "Command to execute",
    choices= ['create', 'send',]
)

parser.add_argument(
    'option',
    help= "Option to command",
    choices= ['facture', ]
)
parser.add_argument('--customer', '-c', type= int, help= "Customer's id")
parser.add_argument(
    '--date',
    '-d',
    help= "Date of task execution",
    default= dt.now().date().strftime('%d-%m-%Y')
)
parser.add_argument(
    '--facture',
    '-f',
    help= "Facture hash"
)

#vybbwpysqpangfdo
args = parser.parse_args()

if __name__ == '__main__':
    if args.command == 'create':
        if args.option == 'facture':
            create_facture(args.customer, args.date)
    elif args.command == 'retrieve':
        pass
    elif args.command == 'send':
        if args.option == 'facture':
            send_facture(args.facture)
    
