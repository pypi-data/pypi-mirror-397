from httpx import Timeout
from typing import TYPE_CHECKING, override

from .types import Cache

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


HEADERS_VERCEL_CACHE_STATE = "x-vercel-cache-state"
HEADERS_VERCEL_REVALIDATE = "x-vercel-revalidate"
HEADERS_VERCEL_CACHE_TAGS = "x-vercel-cache-tags"
HEADERS_VERCEL_CACHE_ITEM_NAME = "x-vercel-cache-item-name"
DEFAULT_TIMEOUT = Timeout(30.0)


class BuildCache(Cache):
    def __init__(self, endpoint: str, headers: Mapping[str, str], /) -> None:
        from httpx import Client
        
        self._endpoint = endpoint.rstrip("/") + "/"
        self._headers = headers
        self._client = Client(timeout=DEFAULT_TIMEOUT)

    @override
    def get(self, key: str, /):
        r = self._client.get(self._endpoint + key, headers=self._headers)
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
            r.close()

    @override
    def set(self, key: str, value: object, /, *, ttl: int | None = None, tags: "Iterable[str] | None" = None) -> None:
        headers = dict(self._headers)
        if ttl:
            headers[HEADERS_VERCEL_REVALIDATE] = str(ttl)
        if tags:
            headers[HEADERS_VERCEL_CACHE_TAGS] = ",".join(tags)

        r = self._client.post(self._endpoint + key, headers=headers, json=value)
        if r.status_code != 200:
            raise RuntimeError(f"Failed to set cache: {r.status_code} {r.reason_phrase}")

    @override
    def delete(self, key: str, /) -> None:
        r = self._client.delete(self._endpoint + key, headers=self._headers)
        if r.status_code != 200:
            raise RuntimeError(f"Failed to delete cache: {r.status_code} {r.reason_phrase}")

    @override
    def expire(self, tag: "str | Iterable[str]", /) -> None:
        tags = tag if isinstance(tag, str) else ",".join(tag)
        r = self._client.post(f"{self._endpoint}revalidate", params={"tags": tags}, headers=self._headers)
        if r.status_code != 200:
            raise RuntimeError(f"Failed to revalidate tag: {r.status_code} {r.reason_phrase}")

    @override
    def contains(self, key: str) -> bool:
        r = self._client.get(self._endpoint + key, headers=self._headers)
        try:
            if r.status_code == 404:
                return False
            if r.status_code != 200:
                raise RuntimeError(f"Failed to get cache: {r.status_code} {r.reason_phrase}")
            cache_state = r.headers.get(HEADERS_VERCEL_CACHE_STATE)
            # Consider present only when fresh
            if cache_state and cache_state.lower() != "fresh":
                return False
            return True
        finally:
            # Ensure the response is closed regardless of outcome
            r.close()

    @override
    def __getitem__(self, key: str, /):
        if key in self:
            return self.get(key)
        raise KeyError(key)
        
    @override
    def __setitem__(self, key: str, value: object, /):
        self.set(key, value)
        
    __delitem__ = delete
    __contains__ = contains
