import json
import os
from typing import TYPE_CHECKING, cast, override

from ._logging import logger
from .cache_in_memory import AsyncInMemoryCache, InMemoryCache
from .context import get_context
from .types import AsyncCache, Cache
from .utils import create_key_transformer

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any, Literal, overload

    from .aio import AsyncBuildCache
    from .cache_build import BuildCache

_in_memory_cache_instance: InMemoryCache | None = None
_async_in_memory_cache_instance: AsyncInMemoryCache | None = None
_build_cache_instance: "BuildCache | None" = None
_async_build_cache_instance: "AsyncBuildCache | None" = None
_warned_cache_unavailable = False


class RuntimeCache(Cache):
    def __init__(
        self,
        /,
        *,
        key_hash_function: "Callable[[str], str] | None" = None,
        namespace: str | None = None,
        separator: str | None = None,
    ) -> None:
        # Transform keys to match get_cache behavior
        self._make_key = create_key_transformer(key_hash_function, namespace, separator)

    @override
    def get(self, key: str, /):
        return _resolve_cache().get(self._make_key(key))

    @override
    def set(self, key: str, value: object, /, **kwargs):
        return _resolve_cache().set(self._make_key(key), value, **kwargs)

    @override
    def delete(self, key: str, /):
        return _resolve_cache().delete(self._make_key(key))

    @override
    def expire(self, tag: "str | Iterable[str]", /):
        # Tag invalidation is not namespaced/hashed by design
        return _resolve_cache().expire(tag)

    @override
    def contains(self, key: str, /) -> bool:
        # Delegate membership to the underlying cache implementation with transformed key
        return self._make_key(key) in _resolve_cache()

    @override
    def __getitem__(self, key: str, /):
        if key in self:
            return self.get(key)
        raise KeyError(key)

    @override
    def __setitem__(self, key: str, value: object, /) -> None:
        return self.set(key, value[0]) if isinstance(value, tuple) else self.set(key, value)

    __delitem__ = delete
    __contains__ = contains


class AsyncRuntimeCache(AsyncCache):
    def __init__(
        self,
        *,
        key_hash_function: Callable[[str], str] | None = None,
        namespace: str | None = None,
        separator: str | None = None,
    ) -> None:
        self._make_key = create_key_transformer(key_hash_function, namespace, separator)

    @override
    async def get(self, key: str, /) -> Any | None:
        return await _resolve_cache(False).get(self._make_key(key))

    @override
    async def set(self, key: str, value: object, /, **kwargs):
        return await _resolve_cache(False).set(self._make_key(key), value, **kwargs)

    @override
    async def delete(self, key: str, /):
        return await _resolve_cache(False).delete(self._make_key(key))

    @override
    async def expire(self, tag: "str | Iterable[str]", /):
        return await _resolve_cache(False).expire(tag)

    @override
    async def contains(self, key: str, /) -> bool:
        return await _resolve_cache(False).contains(self._make_key(key))


def _get_impl(sync: bool = True, /) -> Cache | AsyncCache:
    global _build_cache_instance, _async_build_cache_instance
    if sync and _build_cache_instance:
        return _build_cache_instance
    elif not sync and _async_build_cache_instance:
        return _async_build_cache_instance

    # Prepare a single shared InMemoryCache backing store and an async wrapper over it
    global _in_memory_cache_instance, _async_in_memory_cache_instance
    if _in_memory_cache_instance is None:
        _in_memory_cache_instance = InMemoryCache()
    if _async_in_memory_cache_instance is None:
        _async_in_memory_cache_instance = AsyncInMemoryCache(_in_memory_cache_instance)

    headers = os.getenvb(b"RUNTIME_CACHE_HEADERS")
    endpoint = os.getenv("RUNTIME_CACHE_ENDPOINT") if headers else None
    if not headers or not endpoint:
        global _warned_cache_unavailable
        if not _warned_cache_unavailable:
            logger.warning("Runtime Cache unavailable in this environment. Falling back to in-memory cache.")
            _warned_cache_unavailable = True
        return _in_memory_cache_instance if sync else _async_in_memory_cache_instance

    # Build cache clients
    parsed_headers = json.loads(headers)
    if not isinstance(parsed_headers, dict):
        raise ValueError("RUNTIME_CACHE_HEADERS must be a JSON object")

    if sync:
        if _build_cache_instance is None:
            from .cache_build import BuildCache
            _build_cache_instance = BuildCache(endpoint, parsed_headers)
        return _build_cache_instance
    else:
        if _async_build_cache_instance is None:
            from .aio import AsyncBuildCache
            _async_build_cache_instance = AsyncBuildCache(endpoint, parsed_headers)
        return _async_build_cache_instance


if TYPE_CHECKING:

    @overload
    def _resolve_cache(sync: Literal[True] = ..., /) -> Cache: ...

    @overload
    def _resolve_cache(sync: Literal[False], /) -> AsyncCache: ...


def _resolve_cache(sync: bool = True, /) -> Cache | AsyncCache:
    if cache := getattr(get_context(), "cache", None):
        return cast(Cache, cache) if sync else cast(AsyncCache, cache)
    return _get_impl(sync)
