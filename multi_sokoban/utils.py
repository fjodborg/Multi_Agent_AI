"""Shared utility functions."""
import sys


def println(msg):
    """Print to stderr."""
    print(msg, file=sys.stderr, flush=True)
