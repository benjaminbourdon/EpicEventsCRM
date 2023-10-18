from datetime import datetime
from typing import Optional

import click
from sqlalchemy import select
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import null

from controllers.auth import authentification_required, specified_role_required
from data_validation import ObjectByIDParamType
from data_validation import click_validation as cval
from data_validation import role_support_validation
from models import Contract, Employee, Event, RoleEmployees
from tools import pass_session
from views.lists import print_list_objects, print_object_details
from views.messages import msg_unautorized_action

event_group = click.Group()


@event_group.command()
@click.option(
    "-id",
    "event",
    help="Event's identifiant. Must be an integer linked to an event.",
    required=True,
    prompt="Event's id",
    type=ObjectByIDParamType(Event),
)
def display_event(event: Event):
    print_object_details(event)


@event_group.command()
@click.option(
    "--contract",
    "-co",
    "filter_contract",
    help="Contract id to filter by. Must be an integer linked to a contract.",
    prompt_required=False,
    prompt="Contract's id",
    type=ObjectByIDParamType(Contract),
)
@click.option(
    "--employee",
    "-em",
    "filter_employee",
    help="Support employee id to filter by. Must be an integer linked to an employee.",
    prompt_required=False,
    prompt="Employee's id",
    type=ObjectByIDParamType(Employee),
)
@click.option(
    "--no-support",
    "filter_no_support",
    help="Filter events without support employee associated."
    " Not used if employee filter used as the same time.",
    is_flag=True,
)
@click.option(
    "--followed-events",
    "filter_user_as_support",
    help="Filter events with actual user as support employee associated."
    " Not used if an other employee filter is used as the same time."
    " Restrained to support employees, no effect otherwise.",
    is_flag=True,
)
@authentification_required
@specified_role_required([RoleEmployees.gestion, RoleEmployees.support])
@pass_session
def list_events(
    session: Session,
    user: Employee | None,
    filter_contract: Contract | None = None,
    filter_employee: Employee | None = None,
    filter_no_support: bool = False,
    filter_user_as_support: bool = False,
):
    """List details of events

    Only gestion and support team employees can perform this action."""

    stmt = select(Event)
    if filter_contract is not None:
        stmt = stmt.where(Event.contract == filter_contract)

    if filter_employee is not None:
        stmt = stmt.where(Event.support_employee == filter_employee)
    elif filter_no_support:
        stmt = stmt.where(Event.support_employee == null())
    elif filter_user_as_support and user.role == RoleEmployees.support:
        stmt = stmt.where(Event.support_employee == user)

    events = session.scalars(stmt).all()

    print_list_objects(
        events,
        [
            "id",
            "contrat_id",
            "datetime_start",
            "datetime_end",
            "location",
            "support_employee.username",
            "attendees",
            "notes",
        ],
        title="Liste des contrats",
        headers=[
            "ID évént.",
            "ID Contrat",
            "Date début",
            "Date fin",
            "Lieu",
            "Employé support",
            "Nombre de personnes",
            "Notes",
        ],
        formatters={
            "datetime_start": "%d/%m/%Y",
            "datetime_end": "%d/%m/%Y",
        },
        epilog="""Use "--help" to see avaible filters""",
    )


@event_group.command()
@click.option(
    "--event",
    "-ev",
    "updating_event",
    help="Identifiant of the event. Must be an integer linked to a event.",
    required=True,
    prompt="Event's id",
    type=ObjectByIDParamType(Event),
)
@click.option(
    "--support",
    "-su",
    "support_employee",
    help="Identifiant of the employee from support team. Must be an integer linked to a event.",
    required=True,
    prompt="Support employee's id",
    type=ObjectByIDParamType(Employee),
    callback=cval(role_support_validation),
)
@authentification_required
@specified_role_required([RoleEmployees.gestion])
@pass_session
def add_event_support(
    session: Session,
    user: Employee | None,
    updating_event: Event,
    support_employee: Employee,
):
    """Attach a support employee to an event

    Only gestion team employees can perform this action."""
    updating_event.support_employee = support_employee

    click.echo(
        f"Nouvel employé support id={updating_event.support_employee.id} "
        f"pour l'événement id={updating_event.id}"
    )


@event_group.command()
@click.option(
    "--contract",
    "-co",
    "event_contract",
    help="Identifiant of the contract linked to this event. "
    "Must be an integer linked to a contract.",
    required=True,
    prompt="Contract's id",
    type=ObjectByIDParamType(Contract),
)
@click.option(
    "--date-start",
    "-ds",
    "datetime_start",
    help="Date and time when event starts. Format is '25/02/2000 16:50'",
    required=True,
    prompt="Start of the event",
    type=click.DateTime(formats=["%d/%m/%Y %H:%M"]),
)
@click.option(
    "--end-start",
    "-es",
    "datetime_end",
    help="Date and time when event ends. Format is '25/02/2000 16:50'",
    required=True,
    prompt="End of the event",
    type=click.DateTime(formats=["%d/%m/%Y %H:%M"]),
)
@click.option(
    "--location",
    "-lo",
    "event_location",
    help="Event's location.",
    required=True,
    prompt="Event's location",
)
@click.option(
    "--attendees",
    "-at",
    "number_attendees",
    help="Number of attendees for the event.",
    default=0,
    prompt="Number of attendees",
    type=click.IntRange(min=0),
)
@click.option(
    "--notes",
    "-no",
    "event_notes",
    help="Notes about the event.",
    default="",
    prompt="Notes",
)
@authentification_required
@specified_role_required([RoleEmployees.commercial])
@pass_session
def create_event(
    session: Session,
    user: Employee | None,
    event_contract: Contract,
    datetime_start: datetime,
    datetime_end: datetime,
    event_location: Optional[str] = None,
    number_attendees: Optional[int] = None,
    event_notes: Optional[str] = None,
):
    """Create a new event

    Only commercial team employees can perform this action."""
    new_event = Event(
        contract=event_contract,
        datetime_start=datetime_start,
        datetime_end=datetime_end,
        location=event_location,
        attendees=number_attendees,
        notes=event_notes,
    )

    session.add(new_event)
    session.flush()
    click.echo(f"Nouvel événement id={new_event.id}")


@event_group.command()
@click.option(
    "--event",
    "-ev",
    "updating_event",
    help="Identifiant of the event. Must be an integer linked to a event.",
    required=True,
    prompt="Event's id",
    type=ObjectByIDParamType(Event),
)
@click.option(
    "--date-start",
    "-ds",
    "datetime_start",
    help="Date and time when event starts. Format is '25/02/2000 16:50'",
    prompt="Start of the event",
    prompt_required=False,
    type=click.DateTime(formats=["%d/%m/%Y %H:%M"]),
)
@click.option(
    "--end-start",
    "-es",
    "datetime_end",
    help="Date and time when event ends. Format is '25/02/2000 16:50'",
    prompt_required=False,
    prompt="End of the event",
    type=click.DateTime(formats=["%d/%m/%Y %H:%M"]),
)
@click.option(
    "--location",
    "-lo",
    "event_location",
    help="Event's location.",
    prompt_required=False,
    prompt="Event's location",
)
@click.option(
    "--attendees",
    "-at",
    "number_attendees",
    help="Number of attendees for the event.",
    prompt_required=False,
    prompt="Number of attendees",
    type=click.IntRange(min=0),
)
@click.option(
    "--notes",
    "-no",
    "event_notes",
    help="Notes about the event.",
    prompt_required=False,
    prompt="Notes",
)
@authentification_required
@specified_role_required([RoleEmployees.support])
@pass_session
def update_event(
    session: Session,
    user: Employee | None,
    updating_event: Event,
    datetime_start: Optional[datetime] = None,
    datetime_end: Optional[datetime] = None,
    event_location: Optional[str] = None,
    number_attendees: Optional[int] = None,
    event_notes: Optional[str] = None,
):
    """Modify an existing event

    Only support team employees can perform this action."""

    if updating_event.support_employee != user:
        msg_unautorized_action()
        click.Abort()

    new_values = {
        "datetime_start": datetime_start,
        "datetime_end": datetime_end,
        "location": event_location,
        "attendees": number_attendees,
        "notes": event_notes,
    }
    updating_event.merge_fromdict(new_values)

    click.echo("Événement mis à jour.")
