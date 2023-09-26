import click

from passlib.hash import argon2

from db import get_session
from models import Employee, RoleEmployees
from controllers.auth import authentification_required, specified_role_required
from data_validation import click_validation as cval, username_validation


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
    type=click.Choice(["commercial", "support", "gestion"], case_sensitive=False),
    required=True,
    prompt="New employee's role",
    help="New employee's role.",
)
@authentification_required
@specified_role_required([RoleEmployees.gestion])
def create_employee(
    employee_username, employee_password, employee_role, user: Employee | None
):
    role_equiv = {
        "commercial": RoleEmployees.commercial,
        "support": RoleEmployees.support,
        "gestion": RoleEmployees.gestion,
    }

    new_employee = Employee(
        username=employee_username,
        password=argon2.hash(employee_password),
        role=role_equiv.get(employee_role, None),
    )

    with get_session().begin() as session:
        session.add(new_employee)
        session.flush()
        click.echo(f"Nouvel employée : {new_employee.id}")
