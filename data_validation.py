from typing import Callable, Any

import click


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


class EmployeeRoleParamType(click.Choice):
    name = "employee_role"

    def __init__(self):
        choices = ["commercial", "support", "gestion"]  # Extraire depuis RoleEmployee
        super().__init__(choices, case_sensitive=False)

    def convert(self, value, param, ctx):
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
