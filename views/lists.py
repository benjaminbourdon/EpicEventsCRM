from operator import attrgetter

from click import secho
from prettytable import PrettyTable

from views.messages import print_messages


def get_attr_as_str(object, attr: str, formatter: str | None = None):
    formatter = formatter if formatter is not None else ""
    try:
        return format(attrgetter(attr)(object), formatter)
    except AttributeError:
        return ""


def print_list_objects(
    objects,
    list_attr: list[str],
    formatters: dict[str, str],
    headers: list[str] = None,
    title: str = None,
    epilog: str = None,
):
    """Print in stdout a table with asked attributes from objects."""
    if objects is None or len(objects) == 0:
        print_messages("List is empty", level="warning")
        return

    table = PrettyTable(
        header_style="cap",
        junction_char=" ",
        horizontal_char="–",
    )
    if title:
        table.title = title
    if headers and len(headers) == len(list_attr):
        table.field_names = headers
    for obj in objects:
        table.add_row(
            [
                get_attr_as_str(obj, attr, formatters.get(attr, None))
                for attr in list_attr
            ]
        )
    secho(table.get_string())

    if epilog:
        secho(epilog)
