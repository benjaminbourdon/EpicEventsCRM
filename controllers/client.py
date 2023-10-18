from datetime import datetime
from typing import Optional

import click
from sqlalchemy.orm.session import Session

from controllers.auth import authentification_required, specified_role_required
from data_validation import ObjectByIDParamType
from data_validation import click_validation as cval
from data_validation import email_validation
from models import Client, Employee, RoleEmployees
from tools import pass_session
from views.lists import print_object_details
from views.messages import print_messages, msg_unautorized_action

client_group = click.Group()


@client_group.command()
@click.option(
    "-id",
    "client",
    help="Client's identifiant. Must be an integer linked to a client.",
    required=True,
    prompt="Client's id",
    type=ObjectByIDParamType(Client),
)
def display_client(client: Client):
    print_object_details(client)


@client_group.command()
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
@pass_session
@specified_role_required([RoleEmployees.commercial])
def create_client(
    session: Session,
    user: Optional[Employee],
    client_lastname: str,
    client_firstname: Optional[str] = None,
    client_email: Optional[str] = None,
    client_telephone: Optional[int] = None,
    client_society_name: Optional[str] = None,
):
    """Create a new client

    Only commercial team employees can perform this action."""
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

    session.add(new_client)
    session.flush()
    click.echo(f"Nouveau client : id={new_client.id}")


@client_group.command()
@click.option(
    "-id",
    "updating_client",
    help="Client's identifiant. Must be an integer linked to a client.",
    required=True,
    prompt="Updating client's id",
    type=ObjectByIDParamType(Client),
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
@pass_session
def update_client(
    session: Session,
    user: Optional[Employee],
    updating_client: Client,
    client_lastname: str,
    client_firstname: Optional[str] = None,
    client_email: Optional[str] = None,
    client_telephone: Optional[int] = None,
    client_society_name: Optional[str] = None,
):
    """Modify an existing client

    Only commercial team employees can perform this action."""

    if updating_client.commercial_employee != user:
        msg_unautorized_action()
        click.Abort()

    new_values = {
        "firstname": client_firstname,
        "lastname": client_lastname,
        "email": client_email,
        "tel": client_telephone,
        "society_name": client_society_name,
        "updated_date": datetime.now(),
    }
    updating_client.merge_fromdict(new_values)

    print_messages("Client mis à jour.")
