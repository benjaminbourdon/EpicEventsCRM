import os

import click
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATEBASE_NAME = os.getenv("DATEBASE_NAME")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
DEBUG_MODE = os.getenv("DEBUG_MODE").lower() in ("1", "true")


def get_db_url():
    return URL.create(
        drivername="postgresql+psycopg2",
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        host="localhost",
        database=DATEBASE_NAME,
    )


def get_admin_engine():
    url_object = get_db_url()

    return create_engine(
        url_object,
        # "postgresql+psycopg2://postgres:OC-2023@localhost/test",  # Superuser
        echo=DEBUG_MODE,
    )


def get_admin_session():
    engine = get_admin_engine()

    return sessionmaker(engine)


def get_session(role=None):
    session = get_admin_session()

    # SET ROLE 'name_role'
    # if role == RoleEmployees.commercial:
    #     pass
    # elif role == RoleEmployees.support:
    #     pass
    # elif role == RoleEmployees.support:
    #     pass
    # else:
    #     set role select on employee

    return session


@click.group()
def index():
    pass


@index.command()
def create_tables():
    # Ajouter mdp au superuser (prompt)
    # Creer compte admin
    # Creer roles support, commercial et gestion
    # Ajouter les role au role admin

    import models

    engine = get_admin_engine()
    models.Base.metadata.create_all(engine)


if __name__ == "__main__":
    index()
