import os
from collections import namedtuple
from typing import Literal, TypeAlias

from click import secho
from dotenv import load_dotenv

load_dotenv()

Level: TypeAlias = Literal["default", "warning", "alert", "confirm"]


class MessageSpec(namedtuple("MessageSpec", ["level", "color", "verbosity_min"])):
    __slots__ = ()
    level_specs = {
        "default": {"color": os.getenv("COLOR_DEFAULT"), "verbosity_min": 3},
        "warning": {"color": os.getenv("COLOR_WARNING"), "verbosity_min": 2},
        "alert": {"color": os.getenv("COLOR_ALERT"), "verbosity_min": 1},
        "confirm": {"color": os.getenv("COLOR_CONFIRM"), "verbosity_min": 3},
    }

    def __new__(cls, level: Level = "default"):
        if level not in cls.level_specs:
            level = "default"
        return super().__new__(cls, **({"level": level} | cls.level_specs[level]))


def print_messages(
    message: str,
    level: Level = "default",
    verbosity: int = None,
):
    spec_messag = MessageSpec(level)
    if verbosity is None:
        verbosity = int(os.getenv("DEFAULT_VERBOSITY"))

    if verbosity >= spec_messag.verbosity_min:
        msg_color = spec_messag.color
        secho(message, fg=msg_color)


def msg_authentication_required():
    print_messages("You need to login to do this action.", level="warning")


def msg_unautorized_action():
    print_messages("You don't have rights to process this action.", level="warning")
