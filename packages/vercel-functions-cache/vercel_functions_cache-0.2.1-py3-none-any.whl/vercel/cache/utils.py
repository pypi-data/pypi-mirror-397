from typing import TYPE_CHECKING, Literal

from .context import get_context

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import Any

    HashFunction = Callable[[str], str]
    DefaultNamespaceSeparator = Literal["$"]


def invalidate_by_tag(tag: str | list[str]) -> "Any":
    return api.invalidate_by_tag(tag) if (api := get_context().purge) else None


def dangerously_delete_by_tag(tag: str | Sequence[str], **kwargs) -> Any:
    return api.dangerously_delete_by_tag(tag, **kwargs) if (api := get_context().purge) else None


def __default_hash_func(key: str) -> str:
    # Mirror TS defaultKeyHashFunction: djb2 xor variant, 32-bit unsigned hex
    h = 5381
    for ch in key:
        h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
    return format(h, "x")


def create_key_transformer(func: "HashFunction | None", ns: str | None, sep: str | None = None, /) -> "HashFunction":
    if not func:
        func = __default_hash_func
    if not ns:
        return func

    if not sep:
        sep = "$"
    return lambda key: f"{ns}{sep}{func(key)}"
