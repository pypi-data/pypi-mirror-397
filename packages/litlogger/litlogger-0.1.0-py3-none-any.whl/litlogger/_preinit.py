# Copyright The Lightning AI team.
# Licensed under the Apache License, Version 2.0 (the "License");
#     http://www.apache.org/licenses/LICENSE-2.0
#
"""Pre-initialization wrappers for litlogger to provide helpful error messages."""

from typing import Any, Callable, Optional


class PreInitObject:
    """Object that raises an error if accessed before litlogger.init() is called."""

    def __init__(self, name: str, destination: Optional[Any] = None) -> None:
        self._name = name

        if destination is not None:
            self.__doc__ = destination.__doc__

    def __getitem__(self, key: str) -> None:
        raise RuntimeError(f"You must call litlogger.init() before {self._name}[{key!r}]")

    def __setitem__(self, key: str, value: Any) -> Any:
        raise RuntimeError(f"You must call litlogger.init() before {self._name}[{key!r}]")

    def __setattr__(self, key: str, value: Any) -> Any:
        if not key.startswith("_"):
            raise RuntimeError(f"You must call litlogger.init() before {self._name}.{key}")
        return object.__setattr__(self, key, value)

    def __getattr__(self, key: str) -> Any:
        if not key.startswith("_"):
            raise RuntimeError(f"You must call litlogger.init() before {self._name}.{key}")
        raise AttributeError


def pre_init_callable(name: str, destination: Optional[Any] = None) -> Callable:
    """Create a callable that raises an error if called before litlogger.init()."""

    def preinit_wrapper(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(f"You must call litlogger.init() before {name}()")

    preinit_wrapper.__name__ = str(name)
    if destination:
        preinit_wrapper.__wrapped__ = destination  # type: ignore
        preinit_wrapper.__doc__ = destination.__doc__
    return preinit_wrapper
