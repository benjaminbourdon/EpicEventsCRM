from datetime import datetime
from typing import Optional

import click

from controllers.auth import (
    authentification_required,
    msg_unautorized_action,
    specified_role_required,
)
from data_validation import ObjectByIDParamType
from data_validation import click_validation as cval
from data_validation import role_support_validation
from db import get_session
from models import Contract, Employee, Event, RoleEmployees


@click.group()
def event_group():
    pass


@event_group.command()
@authentification_required
@specified_role_required([RoleEmployees.gestion, RoleEmployees.support])
def list_events(user: Employee | None):
    pass


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
def add_event_support(
    user: Employee | None, updating_event: Event, support_employee: Employee
):
    updating_event.support_employee = support_employee
    with get_session(role=user.role).begin() as session:
        session.add(updating_event)
        session.flush()
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
def create_event(
    user: Employee | None,
    event_contract: Event,
    datetime_start: datetime,
    datetime_end: datetime,
    event_location: Optional[str] = None,
    number_attendees: Optional[int] = None,
    event_notes: Optional[str] = None,
):
    new_event = Event(
        contract=event_contract,
        datetime_start=datetime_start,
        datetime_end=datetime_end,
        location=event_location,
        attendees=number_attendees,
        notes=event_notes,
    )

    with get_session(role=user.role).begin() as session:
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
def update_event(
    user: Employee | None,
    updating_event: Event,
    datetime_start: Optional[datetime] = None,
    datetime_end: Optional[datetime] = None,
    event_location: Optional[str] = None,
    number_attendees: Optional[int] = None,
    event_notes: Optional[str] = None,
):
    with get_session(role=user.role).begin() as session:
        session.add(updating_event)

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

        session.flush()
        click.echo("Événement mis à jour.")