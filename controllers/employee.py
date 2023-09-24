import click

from passlib.hash import argon2

from db import get_session
from models import Employee, RoleEmployees
from controllers.auth import authentification_required, specified_role_required


@click.command()
@click.argument("employee_username")
@click.argument("employee_password")
@click.argument("employee_role")
@authentification_required
@specified_role_required(RoleEmployees.gestion)
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
