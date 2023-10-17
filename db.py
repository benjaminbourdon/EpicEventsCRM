import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATEBASE_NAME = os.getenv("DATEBASE_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DEBUG_MODE = os.getenv("DEBUG_MODE").lower() in ("1", "true")
DB_HOST = os.getenv("DB_HOST")


def get_db_url():
    return URL.create(
        drivername="postgresql+psycopg2",
        username=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        database=DATEBASE_NAME,
    )


def get_admin_engine():
    url_object = get_db_url()

    return create_engine(
        url_object,
        echo=DEBUG_MODE,
    )


def get_session():
    engine = get_admin_engine()

    return sessionmaker(engine)
