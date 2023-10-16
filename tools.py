import click

pass_session = click.decorators.pass_meta_key(key="SESSION", doc_description="")


def atexit_callback(pending, timout):
    """Method which do nothing to overide default callback.
    Default method write in stderr and interfere with cli actions."""
    pass
