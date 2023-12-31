import os
from datetime import datetime, timedelta
from functools import wraps

import click
import jwt
import sentry_sdk
from dotenv import load_dotenv
from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.orm.session import Session

from db import get_session
from models import Employee
from tools import pass_session
from views.messages import msg_authentication_required, msg_unautorized_action
from views.messages import print_messages as mprint

load_dotenv()

SECRET = os.getenv("SECRET")
PATH_TOKEN = os.getenv("PATH_TOKEN")
TOKEN_VALIDITY_HOURS = os.getenv("TOKEN_VALIDITY_HOURS")


auth_group = click.Group()


@auth_group.command()
@click.argument("username")
@click.argument("password")
@pass_session
def login(session: Session, username: str, password: str, persistent: bool = False):
    """Use USERNAME and PASSWORD to log you in

    Use a local JWT token so then you can perform authentification required actions.
    Token has a validity as describe in config file .env"""
    stmt = select(Employee).where(Employee.username == username)
    user = session.scalars(stmt).first()

    if not user or not argon2.verify(secret=password, hash=user.password):
        mprint("Try to login but fail. Try again.", level="warning")
        return

    expiration_date = datetime.now() + timedelta(hours=int(TOKEN_VALIDITY_HOURS))
    payload = {
        "user_id": user.id,
        "user_username": user.username,
        "expiration_timestamp": expiration_date.timestamp(),
    }
    token = jwt.encode(payload=payload, key=SECRET)

    with open(PATH_TOKEN, "w") as file:
        file.write(token)

    mprint("You're now connected.", level="confirm")
    return user


@auth_group.command()
def logoff():
    """Log you off

    Delete local token created when logged in."""
    if os.path.exists(PATH_TOKEN):
        os.remove(PATH_TOKEN)
        click.echo("Succefully logged off.")
    else:
        click.echo("No peristent logging detected. Nothing changed.")


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

        expiration_datetime = datetime.fromtimestamp(payload["expiration_timestamp"])
        if expiration_datetime < datetime.now():
            mprint("Token is expired. You must log again.", level="warning")
            return

        stmt = select(Employee).where(
            Employee.id == user_id, Employee.username == user_username
        )

        ctx = click.get_current_context(silent=True)
        if ctx and "SESSION" in ctx.meta:
            session = ctx.meta["SESSION"]
            assert isinstance(session, Session)
            user = session.execute(stmt).scalar_one_or_none()
        else:
            with get_session().begin() as session:
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
            sentry_sdk.set_user(
                {
                    "id": authentificated_user.id,
                    "username": authentificated_user.username,
                }
            )
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
