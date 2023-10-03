import click

from controllers.auth import login, logoff
from controllers.employee import create_employee, update_employee, deactivate_employee
from controllers.client import create_client, update_client
from controllers.contract import create_contract, update_contract


@click.group()
def index():
    pass


aviable_actions = [
    login,
    logoff,
    create_employee,
    update_employee,
    deactivate_employee,
    create_client,
    update_client,
    create_contract,
    update_contract,
]

for action in aviable_actions:
    index.add_command(action)


if __name__ == "__main__":
    index()
