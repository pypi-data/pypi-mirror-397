from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `apologist.resources` module.

    This is used so that we can lazily import `apologist.resources` only when
    needed *and* so that users can just import `apologist` and reference `apologist.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("apologist.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
