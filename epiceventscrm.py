import click
import os
import sentry_sdk
from dotenv import load_dotenv

from controllers import auth, client, contract, employee, event

load_dotenv()
SENTRY_DSN = os.getenv("SENTRY_DSN")
TRACES_SAMPLE_RATE = float(os.getenv("TRACES_SAMPLE_RATE"))
PROFILES_SAMPLE_RATE = float(os.getenv("PROFILES_SAMPLE_RATE"))


cli = click.CommandCollection(
    sources=[
        auth.auth_group,
        employee.employee_group,
        client.client_group,
        contract.contract_group,
        event.event_group,
    ]
)

if __name__ == "__main__":
    # Initializing Sentry
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=TRACES_SAMPLE_RATE,
        profiles_sample_rate=PROFILES_SAMPLE_RATE,
    )
    cli()
