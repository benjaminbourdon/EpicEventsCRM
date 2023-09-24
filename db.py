import click

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker


DATEBASE_NAME = "test"
ADMIN_USERNAME = "user-app"
ADMIN_PASSWORD = "app-password"


def get_admin_engine():
    url_object = URL.create(
        drivername="postgresql+psycopg2",
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
        host="localhost",
        database=DATEBASE_NAME,
    )

    return create_engine(
        url_object,
        echo=True,
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
    import models

    engine = get_admin_engine()
    models.Base.metadata.create_all(engine)


if __name__ == "__main__":
    index()
