# BeAssist

## But

C'est un petit programme codé en Python, qui pourra vous servir d'assistant dans la gestion de votre structure

## Fichiers

### database.db3

C'est une base de données sqlite pour la persistence des données.
Il contient les tables pour stocker différentes entités comme les clients, les factures, les tâches.

### manage.py

C'est un fichier Python qui gère l'interface en ligne de commande, il contrôle les différentes commandes
et arguments. Il est primordial pour que vous puissiez intéragir avec le programme

### mars.py

C'est le coeur du fonctionnement de tout le programme, il contient les différentes fonctions qui s'exécutent pour la réalisation de chaque tâche.

### orm.py

C'est le fichier qui permet la modélisation et l'interaction avec la base de données. À l'aide du module [peewee](https://github.com/coleifer/peewee).

### setup.py

C'est le fichier d'initialisation du programme sur votre machine. Il se charge de créer la base de données, de la configurer ...

### .env

Bien qu'absent dans le repository, c'est un fichier que vous devrez créer en vous inspirant du template
_.env.exemple_

## Dépendances

Pour faire fonctionner ce programme, vous aurez besoin d'une version de [Python](www.python.org) 3.7+
Vous aurez aussi besoin de la bibliothèque de gestion de pdf [**wkhtmltopdf**](https://wkhtmltopdf.org/downloads.html).

Vous devez l'installer selon l'architecture de votre système et _ajouter le chemin à votre varible d'environnement PATH_

Vous aurez aussi besoin de créer des identifiants OAuth2 dans votre projet, [grâce à cloud google](https://console.cloud.google.com/apis/credentials). Téléchargez ensuite vos clés dans un fichier **credentials.json** dans le répertoire du projet.

## Installation

Pour l'installation, suivez les instructions suivantes.
Notez que la commande _python_ est subtituable à _python3_ suivant votre installation
Dans votre terminal, tapez les commandes suivantes:

1. Clonez ce repository grâce à la commande:
   `git clone https://github.com/ParfaitD9/beassist.git`
2. Rendez vous dans le répertoire beassit en tapant:
   `cd beassist`
3. Créez votre environnement virtuel:
   `python -m venv venv`
4. Installez les modules nécessaires grâce à la commande:
   `pip install -r requirements.txt`
5. Renommer le fichier _.env.exemple_ _.env_ grâce à la commande:
   `mv .env.exemple .env`
6. Modifier le fichier avec vos informations
7. Mettez en place la base de données grâce à la commande:
   `python setup.py`

Voilà, vous venez de finir la mise en place de votre assistant. En cas d'erreur, n'hésitez pas à contacter à le reporter dans les issues.

## Commandes

**Toutes ces commandes supposent que vous soyez dans le dossier beassist.**

- Générer une facture

`python manage.py create facture -c 25 -d 2022-05-01`

Cette commande génère une facture nommée grâce à un algorithme de hachage dans le dossier docs qui est une facture pour les tâches effectués par le client avec l'id 25 à la date du 1er Mai 2022. L'argument -c ou --customer est l'id du client dans la base de données et l'argument -d ou --date est la date d'exécution de la tâche. Plusieurs formats sont supportés pour la date. Si vous ne fournissez pas de date, la date d'aujourd'hui est prise par défaut.

- Envoyer une facture

`python manage.py send facture -f e1bd89ca`

Cette commande envoie la facture e1bd89ca au client concerné.

- Créer un nouveau client

`python manage.py create customer`

Cette commande vous permet de créer un nouvel utilisateur grâce à la ligne de commande. Plusieurs informations vous sont demandées successivement. Saissisez les chaque fois. Vous pouvez arrêter le processus par la commande `Ctrl+C`.

- Supprimer un client

`python manage.py delete customer -c 25`

Cette commande supprimera l'utilisateur avec l'id 25 dans la base de données.
