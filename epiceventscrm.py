import click

from controllers.auth import login, logoff
from controllers.employee import create_employee


@click.group()
def index():
    pass


aviable_actions = [login, logoff, create_employee]

for action in aviable_actions:
    index.add_command(action)


if __name__ == "__main__":
    index()
