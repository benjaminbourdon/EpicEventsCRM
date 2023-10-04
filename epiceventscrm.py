import click

from controllers import auth, employee, client, contract

cli = click.CommandCollection(
    sources=[
        auth.auth_group,
        employee.employee_group,
        client.client_group,
        contract.contract_group,
    ]
)

if __name__ == "__main__":
    cli()
