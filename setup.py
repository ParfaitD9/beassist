from orm import db, Customer, Task, Facture,\
    Pack, PackSubTask, SubTask, City
import os
from orm import DOCS_PATH, COMPTA_PATH
import logging

if __name__ == '__main__':
    try:
        db.connect()
        db.drop_tables([Customer, Task, Facture, Pack,
                       PackSubTask, SubTask])
        db.create_tables([Customer, Task, Facture, Pack,
                         PackSubTask, SubTask, City])
        db.close()
    except Exception as e:
        logging.error(
            f'{e.__class__} : {e.args[0]} durant la création de ma page de données')
    else:
        logging.info('Base de données créée avec succès')

    try:
        with open('.env') as f:
            pass
    except (FileNotFoundError,) as e:
        logging.warning(
            'Create .env file and configure it by *mv .env.exemple .env*.')
    else:
        logging.info('Fichier .env trouvé')

    os.makedirs(DOCS_PATH, exist_ok=True)
    os.makedirs(COMPTA_PATH, exist_ok=True)
    logging.info("Importants paths created")
    City.load_from_csv('./csv/cities.csv')
    Customer.load_from_csv('./csv/customers.csv')
    PackSubTask.load_from_csv()
