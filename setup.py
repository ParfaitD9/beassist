import argparse
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument(
    'cmd',
    choices=('build', 'backup', 'load-backup')
)
parser.add_argument(
    '--reset',
    '-r',
    action=argparse.BooleanOptionalAction,
    default=False
)
parser.add_argument(
    '--backup',
    '-b',
    action=argparse.BooleanOptionalAction,
    default=False
)

parser.add_argument(
    '--deps',
    '-d',
    action=argparse.BooleanOptionalAction,
    default=False
)

parser.add_argument(
    '--init',
    '-i',
    action=argparse.BooleanOptionalAction,
    default=True
)

args = parser.parse_args()
if __name__ == '__main__':
    if args.deps:
        try:
            subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
        except (Exception, ) as e:
            print(f'{e.__class__} : {e.args[0]}')
        else:
            print('Dependences installed successfully')

    from orm import db, Customer, Task, Facture,\
        Pack, PackSubTask, SubTask, City
    import os
    from orm import DOCS_PATH, COMPTA_PATH, CSV_PATH, BACKUP_PATH

    if args.cmd == 'reset':
        try:
            with open('.env') as f:
                pass
        except (FileNotFoundError,) as e:
            print(
                'Create .env file and configure it by *mv .env.exemple .env*.')
        else:
            print('Fichier .env trouvé')
        try:
            with open('.env') as f:
                pass
        except (FileNotFoundError,) as e:
            print(
                'Create .env file and configure it by *mv .env.exemple .env*.')
        else:
            print('Fichier .env trouvé')

        try:
            db.connect()
            db.drop_tables([Customer, Task, Facture, Pack,
                            PackSubTask, SubTask])
            db.create_tables([Customer, Task, Facture, Pack,
                              PackSubTask, SubTask, City])
            db.close()
        except Exception as e:
            print(
                f'{e.__class__} : {e.args[0]} durant la création de ma page de données')
        else:
            print('Base de données créée avec succès')

        for path in (DOCS_PATH, COMPTA_PATH, BACKUP_PATH, CSV_PATH):
            try:
                os.makedirs(path)
            except (FileExistsError, ) as e:
                print(path, 'already exists')
            except (Exception, ) as e:
                print(f"{e.__class__} : {e.args[0]}")
            else:
                print(path, 'crée avec succès')

        print("Importants paths created")
        City.load_from_csv()
        print("Datas loaded")
    elif args.cmd == 'backup':
        Customer.backup()
        Facture.backup()
        SubTask.backup()
        Pack.backup()
        PackSubTask.backup()
    elif args.cmd == 'load-backup':
        Customer.load_backup()
        Facture.load_backup()
        SubTask.load_backup()
        Pack.load_backup()
        PackSubTask.load_backup()
