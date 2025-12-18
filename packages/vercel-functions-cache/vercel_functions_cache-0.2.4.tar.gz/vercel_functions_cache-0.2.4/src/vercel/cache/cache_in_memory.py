from time import time
from typing import TYPE_CHECKING, override

from .types import AsyncCache, Cache

if TYPE_CHECKING:
    from collections.abc import Iterable


class InMemoryCache(Cache):
    def __init__(self) -> None:
        self.__dict: "dict[str, tuple[object, Iterable[str] | None, int | None]]" = {}

    @override
    def get(self, key: str):
        if not (entry := self.__dict.get(key)):
            return None

        expire = entry[2]
        if expire and expire < time():
            self.delete(key)
            return None
        return entry[0]

    @override
    def set(self, key: str, value: object, /, *, ttl: int | None = None, tags: "Iterable[str]" = set()) -> None:
        self.__dict[key] = (value, tags, round(time() + ttl) if ttl else None)

    @override
    def delete(self, key: str) -> None:
        self.__dict.pop(key, None)

    @override
    def contains(self, key: str) -> bool:
        if not (entry := self.__dict.get(key)):
            return False

        expire = entry[2]
        if expire and expire < time():
            self.delete(key)
            return False
        return True

    @override
    def expire(self, tag: "str | Iterable[str]") -> None:
        tags = {tag} if isinstance(tag, str) else set(tag)
        to_delete = set()
        for k, entry in self.__dict.items():
            entry_tags = entry[1]
            if entry_tags and tags.isdisjoint(entry_tags):
                to_delete.add(k)
        for k in to_delete:
            self.__dict.pop(k, None)

    @override
    def __getitem__(self, key: str):
        if key in self:
            return self.get(key)
        raise KeyError(key)

    @override
    def __setitem__(self, key: str, value: object):
        self.set(key, value)

    __delitem__ = delete
    __contains__ = contains


class AsyncInMemoryCache(AsyncCache):
    def __init__(self, delegate: InMemoryCache, /) -> None:
        # Reuse the synchronous implementation under the hood and expose async API
        self.__delegate = delegate

    @override
    async def get(self, key: str, /):
        return self.__delegate.get(key)

    @override
    async def set(self, key: str, value: object, /, **kwargs) -> None:
        self.__delegate.set(key, value, **kwargs)

    @override
    async def delete(self, key: str, /) -> None:
        self.__delegate.delete(key)

    @override
    async def contains(self, key: str, /) -> bool:
        return key in self.__delegate

    @override
    async def expire(self, tag: "str | Iterable[str]", /) -> None:
        self.__delegate.expire(tag)
