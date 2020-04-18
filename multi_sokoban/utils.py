"""Shared utility functions."""
import sys


class ResourceLimit(Exception):
    """Define limit of resources exception."""

    pass


def println(msg):
    """Print to stderr."""
    print(msg, file=sys.stderr, flush=True)
