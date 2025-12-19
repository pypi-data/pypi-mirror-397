from __future__ import annotations

import functools
import warnings


def deprecated_alias(**aliases: str):
    """Decorator to rename deprecated keyword arguments.

    Usage:
        @deprecated_alias(time_limit_sec="solve_limit_sec")
        def solve(..., solve_limit_sec=None, time_limit_sec=None, ...):
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # stacklevel=3: _rename_kwargs -> wrapper -> user code
            _rename_kwargs(func.__name__, kwargs, aliases, stacklevel=3)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _rename_kwargs(
    name: str, kwargs: dict, aliases: dict[str, str], stacklevel: int
) -> None:
    """Rename deprecated keyword arguments to their new names with warnings."""
    for alias, new in aliases.items():
        if alias in kwargs:
            if new in kwargs:
                raise TypeError(
                    f"{name} received both '{alias}' (deprecated) and '{new}'; "
                    f"use only '{new}'"
                )
            warnings.warn(
                f"{alias} is deprecated; use {new}",
                FutureWarning,
                stacklevel=stacklevel,
            )
            kwargs[new] = kwargs.pop(alias)


def check_trailing_metadata_deprecation_warning(call, stacklevel: int) -> None:
    """Check for deprecation warnings in gRPC trailing metadata.

    Args:
        call: gRPC call object with trailing_metadata() method.
        stacklevel: Stack level for warnings.warn().
    """
    if call is None:
        return
    # Iterate as a list to handle multiple warnings with the same key
    for key, value in call.trailing_metadata():
        if key == "deprecation-warning":
            warnings.warn(value, FutureWarning, stacklevel=stacklevel)
