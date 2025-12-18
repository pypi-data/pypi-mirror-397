from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar


_T = TypeVar("_T")

def cache(key: str, /, *, ttl: int | None = None, tags: str | Iterable[str] = ...) -> Callable[[Callable[..., Awaitable[_T]]], Callable[..., Awaitable[_T]]]:
    ...
