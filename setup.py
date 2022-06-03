from orm import db, Customer, Task, Facture,\
    Pack, PackSubTask, SubTask

if __name__ == '__main__':
    try:
        db.connect()
        db.drop_tables([Customer, Task, Facture, Pack, PackSubTask, SubTask])
        db.create_tables([Customer, Task, Facture, Pack,
                         PackSubTask, SubTask])
        db.close()
    except Exception as e:
        print(e, 'during database creation')
    else:
        print('Database created successfully')

    try:
        with open('.env') as f:
            pass
    except (FileNotFoundError,) as e:
        print('Create .env file and configure it properly please.')
    else:
        print('.env file found !')
