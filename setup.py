from orm import db, Customer, Task, Facture,\
    Pack, PackSubTask, SubTask, City
import os
from orm import DOCS_PATH, COMPTA_PATH


if __name__ == '__main__':
    try:
        db.connect()
        db.drop_tables([Customer, Task, Facture, Pack,
                       PackSubTask, SubTask, City])
        db.create_tables([Customer, Task, Facture, Pack,
                         PackSubTask, SubTask, City])
        db.close()
    except Exception as e:
        print(e, 'during database creation')
    else:
        print('Database created successfully')

    try:
        with open('.env') as f:
            pass
    except (FileNotFoundError,) as e:
        print('Create .env file and configure it by *mv .env.exemple .env*.')
    else:
        print('.env file found !')

    os.makedirs(DOCS_PATH, exist_ok=True)
    os.makedirs(COMPTA_PATH, exist_ok=True)
    print("Importants paths created")
