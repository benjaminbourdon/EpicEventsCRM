import click

from controllers.auth import login, logoff


@click.group()
def index():
    pass


aviable_actions = [login, logoff]

for action in aviable_actions:
    index.add_command(action)


if __name__ == "__main__":
    index()
