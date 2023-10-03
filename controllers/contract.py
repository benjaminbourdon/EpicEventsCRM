from datetime import datetime
from typing import Optional

import click

from db import get_session
from models import Contract, RoleEmployees, Employee, Client, ContractStatus
from controllers.auth import authentification_required, specified_role_required
from data_validation import ObjectByIDParamType, EnumClassParamType
from controllers.auth import msg_unautorized_action


@click.command()
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
def create_contract(
    user: Employee | None,
    client_owner: Client,
    total_amount: float,
    remaining_amount: float = None,
):
    if remaining_amount is None:
        remaining_amount = total_amount

    new_contract = Contract(
        client=client_owner,
        total_amount=total_amount,
        amount_to_pay=remaining_amount,
        created_date=datetime.now(),
        status=ContractStatus.pending,
    )

    with get_session(role=user.role).begin() as session:
        session.add(new_contract)
        session.flush()
        click.echo(f"Nouveau contrat créé : id={new_contract.id}")


@click.command()
@click.option(
    "--contract",
    "-co",
    "updating_contract",
    help="Identifiant of the client. Must be an integer linked to a client.",
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
def update_contract(
    user: Employee | None,
    updating_contract: Contract,
    total_amount: Optional[float] = None,
    remaining_amount: Optional[float] = None,
    paiement_status: Optional[ContractStatus] = None,
):
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

    with get_session(role=user.role).begin() as session:
        session.add(updating_contract)
        session.flush()
        click.echo(f"Contrat mis à jour. Status={updating_contract.status.name}")


@click.command()
@authentification_required
@specified_role_required([RoleEmployees.commercial])
def list_contracts(user: Employee | None):
    pass
