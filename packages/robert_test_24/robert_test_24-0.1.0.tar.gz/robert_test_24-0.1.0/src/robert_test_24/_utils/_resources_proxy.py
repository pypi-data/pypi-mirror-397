from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `robert_test_24.resources` module.

    This is used so that we can lazily import `robert_test_24.resources` only when
    needed *and* so that users can just import `robert_test_24` and reference `robert_test_24.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("robert_test_24.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
