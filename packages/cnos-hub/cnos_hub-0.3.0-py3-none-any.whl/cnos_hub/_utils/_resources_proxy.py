from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `cnos_hub.resources` module.

    This is used so that we can lazily import `cnos_hub.resources` only when
    needed *and* so that users can just import `cnos_hub` and reference `cnos_hub.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("cnos_hub.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
