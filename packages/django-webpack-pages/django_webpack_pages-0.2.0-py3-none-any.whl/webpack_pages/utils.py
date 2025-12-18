"""Some utilities."""

import typing

from django.http import HttpRequest


def is_first_visit(request: HttpRequest) -> bool:
    """Assumes that requests without any cookies are first-time requests (used for inlining critical css later)."""
    return len(request.COOKIES) == 0


def conditional_decorator(dec: typing.Callable, *, condition: bool) -> typing.Callable:
    """Conditionally applies decorator.

    Args:
        dec: the original decorator
        condition (bool): the condition

    """

    def decorator(func: typing.Callable) -> typing.Callable:
        if not condition:
            # Return the function unchanged, not decorated.
            return func
        return dec(func)

    return decorator
