from collections.abc import Callable, Iterable
from typing import TypeVar


_T = TypeVar("_T")

def cache(key: str, /, *, ttl: int | None = None, tags: str | Iterable[str] = ...) -> Callable[[Callable[..., _T]], Callable[..., _T]]:
    ...
