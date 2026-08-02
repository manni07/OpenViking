"""Regression tests for the Lark/Uvicorn/WebSockets compatibility boundary."""

from __future__ import annotations

import importlib
import warnings


def test_lark_sdk_no_longer_imports_deprecated_websocket_symbols() -> None:
    """The SDK must not trigger WebSockets legacy-symbol warnings at import."""

    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        importlib.import_module("lark_oapi.ws.client")

    websocket_warnings = [
        warning
        for warning in seen
        if "websocket" in str(warning.message).lower()
        or "websockets" in str(warning.message).lower()
    ]
    assert websocket_warnings == []


def test_uvicorn_sansio_websocket_protocol_imports_without_deprecation() -> None:
    """The selected Uvicorn protocol must avoid the deprecated legacy adapter."""

    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        importlib.import_module("uvicorn.protocols.websockets.auto")
        importlib.import_module("uvicorn.protocols.websockets.websockets_sansio_impl")

    assert [warning for warning in seen if issubclass(warning.category, DeprecationWarning)] == []
