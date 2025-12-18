from httpx import AsyncClient, Limits
from typing import TYPE_CHECKING, override

from .types import AsyncCache
from .cache_build import DEFAULT_TIMEOUT, HEADERS_VERCEL_CACHE_STATE, HEADERS_VERCEL_CACHE_TAGS, HEADERS_VERCEL_REVALIDATE

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

# Use no keep-alive for async clients to avoid lingering background tasks
ASYNC_CLIENT_LIMITS = Limits(max_keepalive_connections=0)


class AsyncBuildCache(AsyncCache):
    def __init__(self, endpoint: str, headers: "Mapping[str, str]", /) -> None:
        self._endpoint = endpoint.rstrip("/") + "/"
        self._headers = headers

    @override
    async def get(self, key: str, /):
        async with AsyncClient(timeout=DEFAULT_TIMEOUT, limits=ASYNC_CLIENT_LIMITS) as client:
            r = await client.get(self._endpoint + key, headers=self._headers)
            try:
                if r.status_code == 404:
                    return None
                if r.status_code != 200:
                    raise RuntimeError(f"Failed to get cache: {r.status_code} {r.reason_phrase}")
                cache_state = r.headers.get(HEADERS_VERCEL_CACHE_STATE)
                if cache_state and cache_state.lower() != "fresh":
                    return None
                return r.json()
            finally:
                await r.aclose()

    @override
    async def set(self, key: str, value: object, /, *, ttl: int | None = None, tags: "Iterable[str] | None" = None) -> None:
        headers = dict(self._headers)
        if ttl:
            headers[HEADERS_VERCEL_REVALIDATE] = str(ttl)
        if tags:
            headers[HEADERS_VERCEL_CACHE_TAGS] = ",".join(tags)

        async with AsyncClient(timeout=DEFAULT_TIMEOUT, limits=ASYNC_CLIENT_LIMITS) as client:
            r = await client.post(self._endpoint + key, headers=headers, json=value)
            if r.status_code != 200:
                await r.aclose()
                raise RuntimeError(f"Failed to set cache: {r.status_code} {r.reason_phrase}")
            await r.aclose()

    @override
    async def delete(self, key: str, /) -> None:
        async with AsyncClient(timeout=DEFAULT_TIMEOUT, limits=ASYNC_CLIENT_LIMITS) as client:
            r = await client.delete(self._endpoint + key, headers=self._headers)
            if r.status_code != 200:
                await r.aclose()
                raise RuntimeError(f"Failed to delete cache: {r.status_code} {r.reason_phrase}")
            await r.aclose()

    @override
    async def expire(self, tag: "str | Iterable[str]", /) -> None:
        tags = tag if isinstance(tag, str) else ",".join(tag)
        async with AsyncClient(timeout=DEFAULT_TIMEOUT, limits=ASYNC_CLIENT_LIMITS) as client:
            r = await client.post(f"{self._endpoint}revalidate", params={"tags": tags}, headers=self._headers)
            if r.status_code != 200:
                await r.aclose()
                raise RuntimeError(f"Failed to revalidate tag: {r.status_code} {r.reason_phrase}")
            await r.aclose()

    @override
    async def contains(self, key: str, /) -> bool:
        async with AsyncClient(timeout=DEFAULT_TIMEOUT, limits=ASYNC_CLIENT_LIMITS) as client:
            r = await client.get(self._endpoint + key, headers=self._headers)
            try:
                if r.status_code == 404:
                    return False
                if r.status_code != 200:
                    raise RuntimeError(f"Failed to get cache: {r.status_code} {r.reason_phrase}")
                cache_state = r.headers.get(HEADERS_VERCEL_CACHE_STATE)
                if cache_state and cache_state.lower() != "fresh":
                    return False
                return True
            finally:
                await r.aclose()
