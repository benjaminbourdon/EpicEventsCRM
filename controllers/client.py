from datetime import datetime
from typing import Optional

import click

from db import get_session
from models import Client, RoleEmployees, Employee
from controllers.auth import authentification_required, specified_role_required
from data_validation import click_validation as cval, email_validation


@click.command()
@click.option(
    "--firstname",
    "-fn",
    "client_firstname",
    help="New client's first name.",
    prompt="New client's first name",
    prompt_required=False,
)
@click.option(
    "--lastname",
    "-ln",
    "client_lastname",
    help="New client last name.",
    required=True,
    prompt="New client's lastname",
)
@click.option(
    "--email",
    "-em",
    "client_email",
    help="New client email adress. Must be a valid adress.",
    prompt="New client's email adress",
    prompt_required=False,
    callback=cval(email_validation, nullable=True),
)
@click.option(
    "--telephone",
    "-te",
    "client_telephone",
    help="New client telephone number. Must be a number only, "
    "with prefix but without '+'. Ex : 33123456789",
    prompt="New client's telephone number",
    prompt_required=False,
    type=click.IntRange(0, 10e14),
)
@click.option(
    "--society",
    "-sn",
    "client_society_name",
    help="New client society name.",
    prompt="New client's society name",
    prompt_required=False,
)
@authentification_required
@specified_role_required([RoleEmployees.commercial])
def create_client(
    user: Optional[Employee],
    client_lastname: str,
    client_firstname: Optional[str] = None,
    client_email: Optional[str] = None,
    client_telephone: Optional[int] = None,
    client_society_name: Optional[str] = None,
):
    new_client = Client(
        firstname=client_firstname,
        lastname=client_lastname,
        tel=client_telephone,
        email=client_email,
        society_name=client_society_name,
        created_date=datetime.now(),
        updated_date=datetime.now(),
        commercial_employee=user,
    )

    with get_session(role=user.role).begin() as session:
        session.add(new_client)
        session.flush()
        click.echo(f"Nouveau client : {new_client.id}")


@click.command()
@click.option(
    "-id",
    "client_id",
    help="Client's identifiant.",
    required=True,
    prompt="Updating client's id",
    type=click.IntRange(min=0, min_open=True),
)
@click.option(
    "--firstname",
    "-fn",
    "client_firstname",
    help="Updated first name.",
    prompt="New first name",
    prompt_required=False,
)
@click.option(
    "--lastname",
    "-ln",
    "client_lastname",
    help="Updated last name.",
    prompt="New last name",
    prompt_required=False,
)
@click.option(
    "--email",
    "-em",
    "client_email",
    help="Updated email adress. Must be a valid adress.",
    prompt="New email adress",
    prompt_required=False,
    callback=cval(email_validation, nullable=True),
)
@click.option(
    "--telephone",
    "-te",
    "client_telephone",
    help="Updated telephone number. Must be a number only, "
    "with prefix but without '+'. Ex : 33123456789",
    prompt="New telephone number",
    prompt_required=False,
    type=click.IntRange(0, 10e14),
)
@click.option(
    "--society",
    "-sn",
    "client_society_name",
    help="Updated society name.",
    prompt="New society name",
    prompt_required=False,
)
@authentification_required
@specified_role_required([RoleEmployees.commercial])
def update_client(
    user: Optional[Employee],
    client_id: int,
    client_lastname: str,
    client_firstname: Optional[str] = None,
    client_email: Optional[str] = None,
    client_telephone: Optional[int] = None,
    client_society_name: Optional[str] = None,
):
    new_values = {
        "firstname": client_firstname,
        "lastname": client_lastname,
        "email": client_email,
        "tel": client_telephone,
        "society_name": client_society_name,
        "updated_date": datetime.now(),
    }

    with get_session(role=user.role).begin() as session:
        target_client = session.get(Client, client_id)
        if target_client is None:
            raise click.UsageError("No existing client with this identifiant.")

        target_client.merge_fromdict(new_values)
        session.flush()
        click.echo(
            f"Client mis à jour : id={target_client.id}, "
            f"username={target_client.firstname}, hash={target_client.lastname}"
        )
