from typing import Optional, Literal
import click

from passlib.hash import argon2

from db import get_session
from models import Employee, RoleEmployees
from controllers.auth import authentification_required, specified_role_required
from data_validation import (
    click_validation as cval,
    username_validation,
    EmployeeRoleParamType,
)


@click.command()
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
    type=EmployeeRoleParamType(),
    required=True,
    prompt="New employee's role",
    help="New employee's role.",
)
@authentification_required
@specified_role_required([RoleEmployees.gestion])
def create_employee(
    employee_username: str,
    employee_password: str,
    employee_role: Literal[RoleEmployees.support],
    user: Optional[Employee],
):
    new_employee = Employee(
        username=employee_username,
        password=argon2.hash(employee_password),
        role=employee_role,
    )

    with get_session(role=user.role).begin() as session:
        session.add(new_employee)
        session.flush()
        click.echo(f"Nouvel employée : {new_employee.id}")


@click.command()
@click.option(
    "-id",
    "employee_id",
    help="Employee's identifiant.",
    required=True,
    prompt="Updating employee's id",
    type=click.IntRange(min=0, min_open=True),
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
    type=EmployeeRoleParamType(),
    default=None,
    prompt="New role",
    prompt_required=False,
    help="Updated role.",
)
@authentification_required
@specified_role_required([RoleEmployees.gestion])
def update_employee(
    user: Optional[Employee],
    employee_id: int,
    employee_username: Optional[str] = None,
    employee_password: Optional[str] = None,
    employee_role: Literal[RoleEmployees.support] = None,
):
    new_values = {
        "username": employee_username,
        "password": argon2.hash(employee_password)
        if employee_password is not None
        else None,
        "role": employee_role,
    }

    with get_session(role=user.role).begin() as session:
        target_employee = session.get(Employee, employee_id)
        target_employee.merge_fromdict(new_values)
        session.flush()
        click.echo(
            f"Employé mis à jour : id={target_employee.id}, "
            f"username={target_employee.username}, hash={target_employee.password}"
        )


@click.command()
@click.option(
    "-id",
    "employee_id",
    help="Employee's identifiant.",
    required=True,
    prompt="Updating employee's id",
    type=click.IntRange(min=0, min_open=True),
)
@authentification_required
@specified_role_required([RoleEmployees.gestion])
@click.confirmation_option()
def deactivate_employee(employee_id: int, user: Employee | None):
    with get_session(role=user.role).begin() as session:
        target_employee = session.get(Employee, employee_id)
        target_employee.password = ""
        session.flush()
        click.echo(
            f"Employé mis à jour : id={target_employee.id}, "
            f"username={target_employee.username}, hash={target_employee.password}"
        )
