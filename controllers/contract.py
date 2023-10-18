from datetime import datetime
from typing import Optional

import click
from sqlalchemy import select
from sqlalchemy.orm.session import Session

from controllers.auth import authentification_required, specified_role_required
from data_validation import EnumClassParamType, ObjectByIDParamType
from models import Client, Contract, ContractStatus, Employee, Event, RoleEmployees
from tools import pass_session
from views.lists import print_list_objects, print_object_details
from views.messages import msg_unautorized_action

contract_group = click.Group()


@contract_group.command()
@click.option(
    "-id",
    "contract",
    help="Contract's identifiant. Must be an integer linked to a contract.",
    required=True,
    prompt="Contract's id",
    type=ObjectByIDParamType(Contract),
)
def display_contract(contract: Contract):
    print_object_details(contract)


@contract_group.command()
@click.option(
    "--client",
    "-cl",
    "client_owner",
    help="Identifiant of the client. Must be an integer linked to a client.",
    required=True,
    prompt="Client's id",
    type=ObjectByIDParamType(Client),
)
@click.option(
    "--total-amount",
    "-ta",
    "total_amount",
    help="Total amount to pay. Must be a number only.",
    required=True,
    prompt="Contrat's total amount",
    type=click.FloatRange(min=0),
)
@click.option(
    "--remaining-amount",
    "-ra",
    "remaining_amount",
    help="Remaining amount to pay. Must be a number only.",
    prompt="Contrat's remaining amount",
    prompt_required=False,
    show_default="total amount",
    type=click.FLOAT,
)
@authentification_required
@specified_role_required([RoleEmployees.gestion])
@pass_session
def create_contract(
    session: Session,
    user: Employee | None,
    client_owner: Client,
    total_amount: float,
    remaining_amount: float = None,
):
    """Create a new contract

    Only gestion team employees can perform this action."""
    if remaining_amount is None:
        remaining_amount = total_amount

    new_contract = Contract(
        client=client_owner,
        total_amount=total_amount,
        amount_to_pay=remaining_amount,
        created_date=datetime.now(),
        status=ContractStatus.pending,
    )

    session.add(new_contract)
    session.flush()
    click.echo(f"Nouveau contrat créé : id={new_contract.id}")


@contract_group.command()
@click.option(
    "--contract",
    "-co",
    "updating_contract",
    help="Identifiant of the client. Must be an integer linked to a contract.",
    required=True,
    prompt="Contract's id",
    type=ObjectByIDParamType(Contract),
)
@click.option(
    "--total-amount",
    "-ta",
    "total_amount",
    help="New total amount to pay. Must be a number only.",
    prompt="Contrat's new total amount",
    prompt_required=False,
    type=click.FloatRange(min=0),
)
@click.option(
    "--remaining-amount",
    "-ra",
    "remaining_amount",
    help="New remaining amount to pay. Must be a number only.",
    prompt="Contrat's new remaining amount",
    prompt_required=False,
    type=click.FLOAT,
)
@click.option(
    "--paiement-status",
    "-ps",
    "paiement_status",
    help="New paiement status.",
    prompt="Contrat's new paiement status",
    prompt_required=False,
    type=EnumClassParamType(ContractStatus),
)
@authentification_required
@specified_role_required([RoleEmployees.gestion, RoleEmployees.commercial])
@pass_session
def update_contract(
    session: Session,
    user: Employee | None,
    updating_contract: Contract,
    total_amount: Optional[float] = None,
    remaining_amount: Optional[float] = None,
    paiement_status: Optional[ContractStatus] = None,
):
    """Modify an existing contract

    Only gestion team and commercial who follow client's contract can use this action.
    """
    if not (
        user.role == RoleEmployees.gestion
        or (
            user.role == RoleEmployees.commercial
            and user == updating_contract.client.commercial_employee
        )
    ):
        msg_unautorized_action()
        raise click.Abort()

    new_values = {
        "total_amount": total_amount,
        "amount_to_pay": remaining_amount,
        "status": paiement_status,
    }
    updating_contract.merge_fromdict(new_values)

    click.echo(f"Contrat mis à jour. Status={updating_contract.status.name}")


@contract_group.command()
@click.option(
    "--client",
    "-cl",
    "filter_client",
    help="Client id to filter by. Must be an integer linked to a client.",
    prompt_required=False,
    prompt="Client's id",
    type=ObjectByIDParamType(Client),
)
@click.option(
    "--event",
    "-ev",
    "filter_event",
    help="Event id to filter by. Must be an integer linked to an event.",
    prompt_required=False,
    prompt="Event's id",
    type=ObjectByIDParamType(Event),
)
@click.option(
    "--after",
    "-af",
    "filter_after",
    help="Date after wich contract has been created. Format is '25/02/2000'",
    prompt_required=False,
    prompt="Start of period to look at",
    type=click.DateTime(formats=["%d/%m/%Y"]),
)
@click.option(
    "--before",
    "-bf",
    "filter_before",
    help="Date before wich contract has been created. Format is '25/02/2000'",
    prompt_required=False,
    prompt="End of period to look at",
    type=click.DateTime(formats=["%d/%m/%Y"]),
)
@authentification_required
@specified_role_required([RoleEmployees.commercial])
@pass_session
def list_contracts(
    session: Session,
    user: Employee | None,
    filter_client: Client | None = None,
    filter_event: Event | None = None,
    filter_after: datetime | None = None,
    filter_before: datetime | None = None,
):
    """List details of contracts

    Only commercial team employees can perform this action."""

    stmt = select(Contract)
    if filter_client is not None:
        stmt = stmt.where(Contract.client == filter_client)
    if filter_event is not None:
        stmt = stmt.where(Contract.associated_event == filter_event)
    if filter_after is not None:
        stmt = stmt.where(Contract.created_date > filter_after)
    if filter_before is not None:
        stmt = stmt.where(Contract.created_date < filter_before)

    contracts = session.scalars(stmt).all()

    print_list_objects(
        contracts,
        [
            "id",
            "created_date",
            "client.fullname",
            "total_amount",
            "amount_to_pay",
            "status.name",
            "associated_event.id",
        ],
        title="Liste des contrats",
        headers=[
            "ID contrat",
            "Date de création",
            "Client",
            "Cout total",
            "Montant dû",
            "Statut",
            "ID événement lié",
        ],
        formatters={
            "created_date": "%d/%m/%Y",
            "amount_to_pay": ".2f",
            "total_amount": ".2f",
        },
        epilog="""Use "--help" to see avaible filters""",
    )
