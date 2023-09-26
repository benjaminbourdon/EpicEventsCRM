import os
from functools import wraps

import click
import jwt
from dotenv import load_dotenv
from passlib.hash import argon2
from sqlalchemy import select

from db import get_session
from models import Employee

load_dotenv()

SECRET = os.getenv("SECRET")
PATH_TOKEN = os.getenv("PATH_TOKEN")


@click.command()
@click.argument("username")
@click.argument("password")
@click.option("--persistent/--no-persistent", default=True)
def login(username, password, persistent=False):
    with get_session().begin() as session:
        stmt = select(Employee).where(Employee.username == username)
        user = session.scalars(stmt).first()

        if not user or not argon2.verify(secret=password, hash=user.password):
            click.secho("Try to login but fail. Try again.", fg="red")
            return

        if persistent:
            # TODO : ajouter une date de perumption au jeton
            payload = {
                "user_id": user.id,
                "user_username": user.username,
            }
            token = jwt.encode(payload=payload, key=SECRET)

            with open(PATH_TOKEN, "w") as file:
                file.write(token)

        return user


@click.command()
def logoff():
    if os.path.exists(PATH_TOKEN):
        os.remove(PATH_TOKEN)
        click.echo("Succefully logged off.")
    else:
        click.echo("No peristent logging detected. Nothing changed.")


def msg_authentication_required():
    click.echo("You need to login to do this action.")


def msg_unautorized_action():
    click.echo("You don't have rights to process this action.")


def get_user_from_token():
    try:
        jwt_token = open(PATH_TOKEN).read()
    except OSError:
        return
    else:
        header_data = jwt.get_unverified_header(jwt_token)
        payload = jwt.decode(
            jwt_token,
            key=SECRET,
            algorithms=[
                header_data["alg"],
            ],
        )

        user_username = payload["user_username"] or None
        user_id = payload["user_id"] or None

        with get_session().begin() as session:
            stmt = select(Employee).where(
                Employee.id == user_id, Employee.username == user_username
            )
            user = session.execute(stmt).scalar_one_or_none()
            session.expunge(user)
            return user


def authentification_required(function):
    @wraps(function)
    def authentificated_action(*args, **kwargs):
        authentificated_user = None
        if "username" and "password" in kwargs:
            username = kwargs["username"]
            password = kwargs["password"]
            authentificated_user = login(username=username, password=password)
        else:
            authentificated_user = get_user_from_token()

        if authentificated_user:
            function(*args, **kwargs, user=authentificated_user)
        else:
            msg_authentication_required()

    return authentificated_action


def specified_role_required(required_roles: list):
    def decorator_verifying_role(function):
        @wraps(function)
        def autorised_action(*args, **kwargs):
            if (
                "user" in kwargs
                and isinstance((user := kwargs["user"]), Employee)
                and user.role in required_roles
            ):
                function(*args, **kwargs)
            else:
                msg_unautorized_action()

        return autorised_action

    return decorator_verifying_role
