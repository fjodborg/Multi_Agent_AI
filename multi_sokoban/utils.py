"""Shared utility functions."""
import sys


class ResourceLimit(Exception):
    """Define limit of resources exception."""

    pass


class IncorrectTask(Exception):
    """Define limit of resources exception."""

    pass


def println(msg):
    """Print to stderr."""
    print(msg, file=sys.stderr, flush=True)


def enum(**named_values):
    """Implement enumeration of options."""
    return type("Enum", (), named_values)


STATUS = enum(ok="Ok", fail="Failed", init="Initialized")
