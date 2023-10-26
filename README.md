# EpicEvent CRM

Ce logiciel fournit un CRM en ligne de commande.
Ce programme utilise principalement les bibliothèque Click.
Les données sont stockées dans une base de données PostgreSQL, 
gérée via l'ORM DQLalchemy. 
Sentry est implementé pour la gestion des logs. 
Enfin, l'authentification est rendue persistente grâce 
à des jetons JWT stockés localement.


## Pré-requis

- Python 3.x (développé avec Python 3.11)

L'ensemble des dépendances sont consultables dans le *Pipfile* ou le fichier *requirements.txt*

## Installation

1. Clonez ce dépôt sur votre machine locale.
``` git clone https://github.com/benjaminbourdon/EpicEventsCRM.git ```
2. Accédez au répertoire du projet. Par exemple, ```cd EPICEVENTCRM```
3. Créez un environnement virtuel.  
La documentation recommande *pipenv*. 
Si *pipenv* est déjà installé sur votre système : 
``` pipenv install ```
Alternativement, avec *venv* :
``` python3 -m venv env ```
4. Activez l'environnement virtuel :
    + Avec *pipenv* : ```pipenv shell```
    + Avec *venv* : 
        + Sur macOS et Linux : ```source env/bin/activate```
        + Sur Windows avec PowerShell : ```env\Scripts\Activate.ps1```
5. Si vous avez choisi *venv*, installez les dépendances manuellement : 
```pip install -r requirements.txt```  
Avec pipenv, les dépendances ont automatiquement été installées lors de la création de l'environnement virtuel. Vous pouvez le vérifier avec :
```pipenv graph```
6. Préciser les variables d'environnement. 
Vous pouvez créer un fichier `.env` à la racine du projet en utilisant le modèle `.env.sample` proposé.
Alternativement, vous pouvez indiquer les variables directment dans votre environnement.
7. Enfin, effectuez la création de la base de données avec l'aide de la librairie alambic :
```alembic upgrade head```

## Utilisation 

-  L'ensemble des commandes disponibles sont disponibles depuis la racine du projet :
```python -m epiceventscrm --help```
-  Globalement, les commandes sont formés sur la base 
`python -m epiceventcrm <command> [options]`
-  Le détail d'utilisation de chaque commande est accessible via son option `--help` :
```python -m epiceventcrm <command> --help```