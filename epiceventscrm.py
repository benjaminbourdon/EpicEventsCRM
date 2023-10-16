import os

import click
import sentry_sdk
from click.core import Context
from dotenv import load_dotenv
from sentry_sdk.integrations.atexit import AtexitIntegration

from controllers import auth, client, contract, employee, event
from db import get_session
from tools import atexit_callback

load_dotenv()
SENTRY_DSN = os.getenv("SENTRY_DSN")
TRACES_SAMPLE_RATE = float(os.getenv("TRACES_SAMPLE_RATE"))
PROFILES_SAMPLE_RATE = float(os.getenv("PROFILES_SAMPLE_RATE"))
DEBUG_MODE = os.getenv("DEBUG_MODE").lower() in ("1", "true")


@click.group(
    cls=click.CommandCollection,
    sources=[
        auth.auth_group,
        employee.employee_group,
        client.client_group,
        contract.contract_group,
        event.event_group,
    ],
)
@click.pass_context
def cli(ctx: Context):
    if not DEBUG_MODE:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=TRACES_SAMPLE_RATE,
            profiles_sample_rate=PROFILES_SAMPLE_RATE,
            debug=DEBUG_MODE,
            integrations=[AtexitIntegration(callback=atexit_callback)],
        )
    ctx.meta["SESSION"] = ctx.with_resource(get_session().begin())
    ctx.meta["SENTRY"] = ctx.with_resource(
        sentry_sdk.start_transaction(name=ctx.invoked_subcommand)
    )


if __name__ == "__main__":
    cli()
