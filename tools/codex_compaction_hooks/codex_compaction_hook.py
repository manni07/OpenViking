# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0
"""Small, fail-closed Codex compaction hook.

Hook input is untrusted.  Only fixed messages are returned to Codex, while a
private, bounded correlation record is kept below ``CODEX_HOME``.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess  # noqa: F401 - tests prove the critical path never uses it.
import sys
import time
import uuid
from pathlib import Path
from typing import Any

STATE_SUBDIRECTORY = "state/compaction-hooks"
MAX_STDIN_BYTES = 64 * 1024
INTERNAL_TIMEOUT_SECONDS = 5.0

_SUCCESS = {
    "continue": True,
    "systemMessage": (
        "Continue from the compacted context. Preserve explicit stop conditions "
        "and verify required evidence before claiming completion."
    ),
}
_SESSION_COMPACT = {
    "continue": True,
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": (
            "Compaction continuity: preserve explicit stop conditions and verify "
            "required evidence before claiming completion."
        ),
    },
}
_NO_CONTEXT = {"continue": True}
_FAILURE = {
    "continue": False,
    "stopReason": "Compaction hook invariant check failed.",
}


def _digest(value: Any) -> str:
    text = value if isinstance(value, str) else ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ensure_private_directory(path: Path, boundary: Path) -> None:
    """Create ``path`` without accepting symlinked or foreign-owned components."""
    try:
        relative = path.relative_to(boundary)
    except ValueError as exc:
        raise OSError("state directory escapes CODEX_HOME") from exc

    missing: list[Path] = []
    cursor = path
    while True:
        if cursor.is_symlink():
            raise OSError("unsafe state directory")
        if cursor.exists():
            break
        if cursor == boundary.parent:
            raise OSError("unsafe CODEX_HOME boundary")
        missing.append(cursor)
        cursor = cursor.parent

    for component in reversed(missing):
        component.mkdir(mode=0o700, exist_ok=True)

    expected_owner = os.geteuid()
    components = [boundary]
    cursor = boundary
    for part in relative.parts:
        cursor /= part
        components.append(cursor)
    for cursor in components:
        info = cursor.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise OSError("unsafe state directory")
        if info.st_uid != expected_owner:
            raise OSError("unsafe state directory owner")
        if cursor == path:
            os.chmod(cursor, 0o700)

    info = path.lstat()
    if info.st_mode & 0o777 != 0o700:
        raise OSError("unsafe state directory permissions")


def _record_path(state_root: Path, event: dict[str, Any]) -> Path:
    correlation = hashlib.sha256(
        (_digest(event.get("session_id")) + ":" + _digest(event.get("turn_id"))).encode("ascii")
    ).hexdigest()
    return state_root / f"{correlation}.json"


def _atomic_write(record_path: Path, payload: dict[str, Any]) -> None:
    state_root = record_path.parent
    if record_path.is_symlink():
        raise OSError("unsafe record target")
    if record_path.exists():
        info = record_path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
            raise OSError("unsafe record target")

    temp_path = state_root / f".{record_path.stem}.{uuid.uuid4().hex}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(temp_path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, 0o600)
        if record_path.is_symlink():
            raise OSError("unsafe record target")
        os.replace(temp_path, record_path)
        os.chmod(record_path, 0o600)
        directory_fd = os.open(state_root, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def _read_record(record_path: Path) -> dict[str, Any]:
    info = record_path.lstat()
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or info.st_uid != os.geteuid()
        or info.st_mode & 0o777 != 0o600
    ):
        raise OSError("unsafe record")
    if info.st_size > 4096:
        raise OSError("oversized record")
    with record_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("invalid record")
    return value


def process_event(
    event: dict[str, Any],
    *,
    codex_home: Path | str | None = None,
) -> dict[str, Any]:
    started = time.monotonic()
    if not isinstance(event, dict):
        return dict(_FAILURE)

    event_name = event.get("hook_event_name")
    if event_name == "SessionStart":
        return dict(_SESSION_COMPACT if event.get("source") == "compact" else _NO_CONTEXT)
    if event_name not in {"PreCompact", "PostCompact"}:
        return dict(_FAILURE)

    try:
        base = Path(
            codex_home
            if codex_home is not None
            else os.environ.get("CODEX_HOME", "").strip() or Path.home() / ".codex"
        )
        state_root = base / STATE_SUBDIRECTORY
        _ensure_private_directory(state_root, base)
        record_path = _record_path(state_root, event)
        session_digest = _digest(event.get("session_id"))
        turn_digest = _digest(event.get("turn_id"))
        if not event.get("session_id") or not event.get("turn_id"):
            raise ValueError("missing correlation")

        if event_name == "PreCompact":
            _atomic_write(
                record_path,
                {
                    "schema": 1,
                    "session": session_digest,
                    "turn": turn_digest,
                    "prepared": True,
                },
            )
        else:
            record = _read_record(record_path)
            if (
                record.get("schema") != 1
                or record.get("session") != session_digest
                or record.get("turn") != turn_digest
                or record.get("prepared") is not True
            ):
                raise ValueError("correlation mismatch")
            _atomic_write(
                record_path,
                {
                    "schema": 1,
                    "session": session_digest,
                    "turn": turn_digest,
                    "prepared": True,
                    "completed": True,
                },
            )

        if time.monotonic() - started >= INTERNAL_TIMEOUT_SECONDS:
            raise TimeoutError("internal deadline")
        return dict(_SUCCESS)
    except Exception:
        return dict(_FAILURE)


def main() -> int:
    payload = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
    if len(payload) > MAX_STDIN_BYTES:
        output = dict(_FAILURE)
        status = 2
    else:
        try:
            event = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            event = None
        output = process_event(event)
        status = 0 if output.get("continue") is True else 2
    sys.stdout.write(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
