from typing import Literal, Optional

import click
from passlib.hash import argon2
from sqlalchemy.orm.session import Session

from controllers.auth import authentification_required, specified_role_required
from data_validation import EnumClassParamType, ObjectByIDParamType
from data_validation import click_validation as cval
from data_validation import username_validation
from models import Employee, RoleEmployees
from tools import pass_session


@click.group()
def employee_group():
    pass


@employee_group.command()
@click.option(
    "--username",
    "-un",
    "employee_username",
    help="New employee's username. Must be an alphanumeric string of 30 caracters or less.",
    required=True,
    prompt="New employee's username",
    callback=cval(username_validation),
)
@click.option(
    "--password",
    "-pw",
    "employee_password",
    required=True,
    prompt="New employee's password",
    hide_input=True,
    confirmation_prompt=True,
    help="New employee's password.",
)
@click.option(
    "--role",
    "-ro",
    "employee_role",
    type=EnumClassParamType(RoleEmployees),
    required=True,
    prompt="New employee's role",
    help="New employee's role.",
)
@authentification_required
@specified_role_required([RoleEmployees.gestion])
@pass_session
def create_employee(
    session: Session,
    employee_username: str,
    employee_password: str,
    employee_role: Literal[RoleEmployees.support],
    user: Optional[Employee],
):
    """Create a new employee

    Only gestion team employees can perform this action."""
    new_employee = Employee(
        username=employee_username,
        password=argon2.hash(employee_password),
        role=employee_role,
    )

    session.add(new_employee)
    session.flush()
    click.echo(f"Nouvel employée : {new_employee.id}")


@employee_group.command()
@click.option(
    "-id",
    "updating_employee",
    help="Employee's identifiant. Must be an integer linked to an employee",
    required=True,
    prompt="Updating employee's id",
    type=ObjectByIDParamType(Employee),
)
@click.option(
    "--username",
    "-un",
    "employee_username",
    help="Updated username. Must be an alphanumeric string of 30 caracters or less.",
    default=None,
    prompt="New username",
    prompt_required=False,
    callback=cval(username_validation),
)
@click.option(
    "--password",
    "-pw",
    "employee_password",
    default=None,
    prompt="New password",
    prompt_required=False,
    hide_input=True,
    confirmation_prompt=True,
    help="Updated password.",
)
@click.option(
    "--role",
    "-ro",
    "employee_role",
    type=EnumClassParamType(RoleEmployees),
    default=None,
    prompt="New role",
    prompt_required=False,
    help="Updated role.",
)
@authentification_required
@specified_role_required([RoleEmployees.gestion])
@pass_session
def update_employee(
    session: Session,
    user: Optional[Employee],
    updating_employee: Employee,
    employee_username: Optional[str] = None,
    employee_password: Optional[str] = None,
    employee_role: Literal[RoleEmployees.support] = None,
):
    """Modify an existing employee

    Only gestion team employees can perform this action."""
    new_values = {
        "username": employee_username,
        "password": argon2.hash(employee_password)
        if employee_password is not None
        else None,
        "role": employee_role,
    }

    updating_employee.merge_fromdict(new_values)

    click.echo(
        f"Employé mis à jour : id={updating_employee.id}, "
        f"username={updating_employee.username}, role={updating_employee.role}"
    )


@employee_group.command()
@click.option(
    "-id",
    "deleting_employee",
    help="Employee's identifiant. Must be an integer linked to an employee.",
    required=True,
    prompt="Updating employee's id",
    type=ObjectByIDParamType(Employee),
)
@authentification_required
@specified_role_required([RoleEmployees.gestion])
@click.confirmation_option()
@pass_session
def deactivate_employee(
    session: Session, deleting_employee: Employee, user: Employee | None
):
    """Deactivate an employee

    A deactivated employee can no longer log in.
    To reactivate an employee, use "update-employee" and set a new password.

    Only gestion team employees can perform this action."""

    deleting_employee.password = ""
    click.echo(
        f"Employé mis à jour : id={deleting_employee.id}, "
        f"username={deleting_employee.username}, hash={deleting_employee.password}"
    )
