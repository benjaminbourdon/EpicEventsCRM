import os
from typing import Any, Callable

import click
from click.core import Context, Parameter
from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email
from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept

from db import get_admin_session

load_dotenv()
DEBUG_MODE = os.getenv("DEBUG_MODE").lower() in ("1", "true")


def click_validation(validation_function: Callable, nullable=True) -> Callable:
    def callback_validation_function(ctx, param, value):
        if nullable and value is None:
            return value

        is_valid, result = validation_function(value)

        if is_valid:
            return result
        else:
            raise click.BadParameter(result)

    return callback_validation_function


def username_validation(username: str) -> tuple[bool, str]:
    if not username.isalnum():
        return (False, "Must be an alphanumeric string. No special caracter allowed.")
    if len(username) > 30:
        return (False, "Must be 30 caracters or less.")

    return (True, username)


def role_validation(role) -> tuple[bool, Any | str]:
    from models import RoleEmployees

    try:
        if role in RoleEmployees:
            return (True, role)
    except TypeError:
        pass

    if isinstance(role, str) and role in (role_equiv := RoleEmployees.role_equiv):
        return (True, role_equiv[role])

    return (False, f"{str(role)} isn't a known role.")


def email_validation(email: str) -> tuple[bool, Any | str]:
    try:
        emailinfo = validate_email(
            email,
            check_deliverability=False,
            test_environment=DEBUG_MODE,
        )
    except EmailNotValidError as e:
        return (False, str(e))
    else:
        return (True, emailinfo.normalized)


class EmployeeRoleParamType(click.Choice):
    name = "employee_role"

    def __init__(self):
        choices = ["commercial", "support", "gestion"]  # Extraire depuis RoleEmployee
        super().__init__(choices, case_sensitive=False)

    def convert(self, value: Any, param: Parameter | None, ctx: Context | None) -> Any:
        from models import RoleEmployees

        try:
            if value in RoleEmployees:
                return value
        except TypeError:
            pass

        if isinstance(value, str):
            normalized_value = super().convert(value, param, ctx)

            if normalized_value in (role_equiv := RoleEmployees.role_equiv):
                return role_equiv[normalized_value]

        self.fail(f"{str(value)} isn't a known role.", param, ctx)


class ObjectByIDParamType(click.ParamType):
    name = "object_by_id"

    _db_object_class = None

    @property
    def db_object_class(self):
        return self._db_object_class

    @db_object_class.setter
    def db_object_class(self, value):
        if isinstance(value, DeclarativeAttributeIntercept):
            self._db_object_class = value
        else:
            raise ValueError(f"{type(value)} isn't a valid model class.")

    @db_object_class.deleter
    def db_object_class(self):
        self._db_object_class = None

    def __init__(self, db_object_cls):
        super().__init__()
        self.db_object_class = db_object_cls

    def convert(self, value: Any, param: Parameter | None, ctx: Context | None) -> Any:
        if isinstance(value, self.db_object_class):
            return value

        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                self.fail(
                    f""""{value}" isn't a valid identifiant, must be an integer.""",
                    param,
                    ctx,
                )
        if isinstance(value, int):
            object_id = value
            with get_admin_session().begin() as session:
                result = session.get(self.db_object_class, object_id)
                if result is None:
                    self.fail(
                        f"No {self.db_object_class.__name__} object has id={object_id}.",
                        param,
                        ctx,
                    )
                else:
                    session.expunge(result)
                    return result

        self.fail(f"{value} is not valid.", param, ctx)
