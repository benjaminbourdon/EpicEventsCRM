import enum
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
    """Transform a validation method in a click callback

    A wrapper wich take a validation function
    and return a standart callback function usable for click options.
    """

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
    """Validate username option

    Check for lenght (max 30) and alphanumeric only."""
    if not username.isalnum():
        return (False, "Must be an alphanumeric string. No special caracter allowed.")
    if len(username) > 30:
        return (False, "Must be 30 caracters or less.")

    return (True, username)


def email_validation(email: str) -> tuple[bool, Any | str]:
    """Validate email option"""
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


def role_support_validation(employee) -> tuple[bool, Any | str]:
    """Validate that an employee is from support team"""
    from models import RoleEmployees

    if employee.role == RoleEmployees.support:
        return (True, employee)
    else:
        return (False, "This employee isn't in support team.")


class EnumClassParamType(click.Choice):
    """Type for click options which use an enum class"""

    name = "enumclass_paramtype"

    def __init__(self, enum_class: enum.Enum):
        self.enum_class = enum_class
        self.choices_dict = {items.name: items for items in enum_class}
        super().__init__(choices=self.choices_dict.keys(), case_sensitive=False)

    def convert(self, value: Any, param: Parameter | None, ctx: Context | None) -> Any:
        """Return an attribute of an enum class

        Can use the name of the attribute to return the according object"""
        try:
            if value in self.enum_class:
                return value
        except TypeError:
            pass

        if isinstance(value, str):
            normalized_value = super().convert(value, param, ctx)

            if normalized_value in self.choices_dict:
                return self.choices_dict[normalized_value]

        self.fail(f"{str(value)} isn't a known role.", param, ctx)


class ObjectByIDParamType(click.ParamType):
    """ "Type for click options wich use object's identifiant"""

    name = "object_by_id"

    _db_object_class = None

    @property
    def db_object_class(self):
        return self._db_object_class

    @db_object_class.setter
    def db_object_class(self, value):
        # Verify specified value is a class who inherit from a declarative base class
        # It's a minimum specification for a model to be translate into database
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
        """Return an DB_OBJECT_CLASS object from database

        Can use integer identifiant to return the targeted object"""
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
