import click
import os
import sentry_sdk
from sentry_sdk.integrations.atexit import AtexitIntegration
from dotenv import load_dotenv

from controllers import auth, client, contract, employee, event

load_dotenv()
SENTRY_DSN = os.getenv("SENTRY_DSN")
TRACES_SAMPLE_RATE = float(os.getenv("TRACES_SAMPLE_RATE"))
PROFILES_SAMPLE_RATE = float(os.getenv("PROFILES_SAMPLE_RATE"))
DEBUG_MODE = os.getenv("DEBUG_MODE").lower() in ("1", "true")

cli = click.CommandCollection(
    sources=[
        auth.auth_group,
        employee.employee_group,
        client.client_group,
        contract.contract_group,
        event.event_group,
    ],
)


def atexit_callback(pending, timout):
    """Method which do nothing to overide default callback.
    Default method write in stderr and interfere with cli actions."""
    pass


if __name__ == "__main__":
    if not DEBUG_MODE:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=TRACES_SAMPLE_RATE,
            profiles_sample_rate=PROFILES_SAMPLE_RATE,
            debug=DEBUG_MODE,
            integrations=[AtexitIntegration(callback=atexit_callback)],
        )
    cli()
