import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '--reset',
    '-r',
    action=argparse.BooleanOptionalAction,
    default=False
)
args = parser.parse_args()
if __name__ == '__main__':
    import subprocess

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

    try:
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
    except (Exception, ) as e:
        print(f'{e.__class__} : {e.args[0]}')
    else:
        print('Dependences installed successfully')

    if args.reset:
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

        try:
            with open('.env') as f:
                pass
        except (FileNotFoundError,) as e:
            print(
                'Create .env file and configure it by *mv .env.exemple .env*.')
        else:
            print('Fichier .env trouvé')

        for path in (DOCS_PATH, COMPTA_PATH, BACKUP_PATH, CSV_PATH):
            print('Path is ', path)
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
        Customer.load_from_csv()
        PackSubTask.load_from_csv()

        print("Datas loaded")
