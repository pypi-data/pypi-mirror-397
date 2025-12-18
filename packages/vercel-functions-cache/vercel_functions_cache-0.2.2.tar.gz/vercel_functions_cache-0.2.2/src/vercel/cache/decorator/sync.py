from typing import TYPE_CHECKING

from vercel.cache.runtime_cache import RuntimeCache


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    CacheDecorator = Callable[[Callable[..., object]], Callable[..., object]]

def cache(key: str, /, *, ttl: int | None = None, tags: "str | Iterable[str]" = set()) -> "CacheDecorator":
    def wrapper(func):
        value = None
        def get():
            nonlocal value
            if value:
                return value

            value = RuntimeCache().get(key)
            if value is None:
                value = func()
                RuntimeCache().set(key, value, ttl=ttl, tags=tags)
            return value
        return get
    return wrapper
