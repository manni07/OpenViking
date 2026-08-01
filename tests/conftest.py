# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0

"""Global test fixtures"""

# Standalone live-test projects with their own environments and workflows.
collect_ignore = ["api_test", "oc2ov_test"]

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio

# Bootstrap imports against a disposable, non-host config.  Several OpenViking
# modules configure their logger during import; waiting for a function fixture
# would be too late to prevent a host ``~/.openviking/ov.conf`` read.
_CONFIG_ENV_NAME = "OPENVIKING_CONFIG_FILE"
_BOOTSTRAP_TMP = tempfile.TemporaryDirectory(prefix="openviking-root-config-")
_BOOTSTRAP_CONFIG_PATH = Path(_BOOTSTRAP_TMP.name) / "ov.conf"
_BOOTSTRAP_WORKSPACE = Path(_BOOTSTRAP_TMP.name) / "workspace"
_BOOTSTRAP_CONFIG_PATH.write_text(
    json.dumps(
        {
            "storage": {
                "workspace": str(_BOOTSTRAP_WORKSPACE),
                "agfs": {"backend": "local"},
                "vectordb": {"name": "test", "backend": "local", "project": "default"},
            },
            "embedding": {
                "dense": {"provider": "litellm", "model": "root-bootstrap", "dimension": 3}
            },
            "vlm": {"provider": None, "model": None},
        }
    ),
    encoding="utf-8",
)
os.environ[_CONFIG_ENV_NAME] = str(_BOOTSTRAP_CONFIG_PATH)

from openviking import AsyncOpenViking
from openviking.models.embedder.base import DenseEmbedderBase, EmbedResult
from openviking_cli.utils.config import OPENVIKING_CONFIG_ENV
from openviking_cli.utils.config.embedding_config import EmbeddingConfig
from openviking_cli.utils.config.open_viking_config import OpenVikingConfigSingleton
from openviking_cli.utils.config.vlm_config import VLMConfig


# ── Workaround: local .so may lack AGFS_Grep symbol (new in latest source) ──
def _patch_agfs_grep_if_missing():
    """Wrap _setup_functions to catch missing AGFS_Grep and skip its binding."""
    try:
        from openviking.pyagfs.binding_client import BindingLib

        _orig_setup = BindingLib._setup_functions

        def _safe_setup(self):
            try:
                _orig_setup(self)
            except AttributeError as e:
                if "AGFS_Grep" not in str(e):
                    raise
                # Re-implement _setup_functions but skip AGFS_Grep lines.
                # We do this by temporarily removing the Grep lines from the
                # source, but since we can't edit .so, we monkey-patch the lib
                # object's __getattr__ to not fail on AGFS_Grep.
                import ctypes

                class _GrepStub:
                    """Fake ctypes function descriptor for AGFS_Grep."""

                    argtypes = [
                        ctypes.c_int64,
                        ctypes.c_char_p,
                        ctypes.c_char_p,
                        ctypes.c_int,
                        ctypes.c_int,
                        ctypes.c_int,
                        ctypes.c_int,
                    ]
                    restype = ctypes.c_char_p

                    def __call__(self, *args):
                        return b'{"error":"AGFS_Grep not available in this .so version"}'

                # Patch at the CDLL instance level by overriding __getattr__
                orig_class = type(self.lib)
                orig_getattr = orig_class.__getattr__

                def patched_getattr(cdll_self, name):
                    if name == "AGFS_Grep":
                        return _GrepStub()
                    return orig_getattr(cdll_self, name)

                orig_class.__getattr__ = patched_getattr
                try:
                    _orig_setup(self)
                finally:
                    orig_class.__getattr__ = orig_getattr

        BindingLib._setup_functions = _safe_setup
    except Exception:
        pass


_patch_agfs_grep_if_missing()

@pytest.fixture(scope="session")
def event_loop():
    """Create session-level event loop"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def temp_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create pytest-owned storage isolated from other tests and workers."""
    root = tmp_path / "root"
    root.mkdir()
    yield root


@pytest.fixture(scope="function")
def test_data_dir(temp_dir: Path) -> Path:
    """Create test data directory"""
    data_dir = temp_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture(scope="function")
def sample_text_file(temp_dir: Path) -> Path:
    """Create sample text file"""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("This is a sample text file for testing OpenViking.")
    return file_path


@pytest.fixture(scope="function")
def sample_markdown_file(temp_dir: Path) -> Path:
    """Create sample Markdown file"""
    file_path = temp_dir / "sample.md"
    file_path.write_text(
        """# Sample Document

## Introduction
This is a sample markdown document for testing OpenViking.

## Features
- Feature 1: Resource management
- Feature 2: Semantic search
- Feature 3: Session management

## Usage
Use this document to test various OpenViking functionalities.
"""
    )
    return file_path


@pytest.fixture(scope="function")
def sample_skill_file(temp_dir: Path) -> Path:
    """Create sample skill file in SKILL.md format"""
    file_path = temp_dir / "sample_skill.md"
    file_path.write_text(
        """---
name: sample-skill
description: A sample skill for testing OpenViking skill management
tags:
  - test
  - sample
---

# Sample Skill

## Description
A sample skill for testing OpenViking skill management.

## Usage
Use this skill when you need to test skill functionality.

## Instructions
1. Step one: Initialize the skill
2. Step two: Execute the skill
3. Step three: Verify the result
"""
    )
    return file_path


@pytest.fixture(scope="function")
def sample_directory(temp_dir: Path) -> Path:
    """Create sample directory with multiple files"""
    dir_path = temp_dir / "sample_dir"
    dir_path.mkdir(parents=True, exist_ok=True)

    (dir_path / "file1.txt").write_text("Content of file 1 for testing.")
    (dir_path / "file2.md").write_text("# File 2\nContent of file 2 for testing.")

    subdir = dir_path / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Content of file 3 in subdir for testing.")

    return dir_path


@pytest.fixture(scope="function")
def sample_files(temp_dir: Path) -> list[Path]:
    """Create multiple sample files for batch testing"""
    files = []
    for i in range(3):
        file_path = temp_dir / f"batch_file_{i}.md"
        file_path.write_text(
            f"""# Batch File {i}

## Content
This is batch file number {i} for testing batch operations.

## Keywords
- batch
- test
- file{i}
"""
        )
        files.append(file_path)
    return files


# ============ Client Fixtures ============


@pytest_asyncio.fixture(scope="function")
async def root_openviking_config(
    test_data_dir: Path, monkeypatch
) -> AsyncGenerator[dict, None]:
    """Install a function-scoped, offline config before embedded clients are built.

    The host ``ov.conf`` is intentionally not read by this fixture.  A direct
    config dictionary also keeps provider endpoints and credentials out of the
    root test process.
    """
    await AsyncOpenViking.reset()
    OpenVikingConfigSingleton.reset_instance()

    workspace = test_data_dir.resolve()
    config = {
        "default_account": "root-fixture",
        "default_user": "root-fixture",
        "storage": {
            "workspace": str(workspace),
            "agfs": {"backend": "local"},
            "vectordb": {"name": "test", "backend": "local", "project": "default"},
        },
        "embedding": {
            "dense": {
                "provider": "litellm",
                "model": "test-offline",
                "dimension": 3,
            }
        },
        "vlm": {"provider": None, "model": None},
    }
    config_path = test_data_dir.parent / "ov.conf"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    monkeypatch.setenv(OPENVIKING_CONFIG_ENV, str(config_path))
    for env_name in (
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "OPENVIKING_EMBEDDING_API_KEY",
        "OPENVIKING_VLM_API_KEY",
    ):
        monkeypatch.delenv(env_name, raising=False)

    class RootFixtureEmbedder(DenseEmbedderBase):
        def __init__(self):
            super().__init__(model_name="root-fixture-embedder", config={"provider": "test"})

        def embed(self, content, is_query: bool = False) -> EmbedResult:
            return EmbedResult(dense_vector=[0.0, 0.0, 0.0])

        def get_dimension(self) -> int:
            return 3

    async def _fake_completion(*_args, **_kwargs) -> str:
        return "# Root fixture summary"

    async def _fake_vision_completion(*_args, **_kwargs) -> str:
        return "Root fixture image summary"

    monkeypatch.setattr(EmbeddingConfig, "get_embedder", lambda _self: RootFixtureEmbedder())
    monkeypatch.setattr(VLMConfig, "is_available", lambda _self: True)
    monkeypatch.setattr(VLMConfig, "get_completion_async", _fake_completion)
    monkeypatch.setattr(VLMConfig, "get_vision_completion_async", _fake_vision_completion)

    try:
        OpenVikingConfigSingleton.initialize(config_dict=config)
        yield config
    finally:
        await AsyncOpenViking.reset()
        OpenVikingConfigSingleton.reset_instance()


@pytest_asyncio.fixture(scope="function")
async def client(
    test_data_dir: Path, root_openviking_config
) -> AsyncGenerator[AsyncOpenViking, None]:
    """Create initialized OpenViking client"""
    await AsyncOpenViking.reset()

    client = AsyncOpenViking(path=str(test_data_dir))
    await client.initialize()

    yield client

    try:
        await client.close()
    finally:
        await AsyncOpenViking.reset()


@pytest_asyncio.fixture(scope="function")
async def uninitialized_client(
    test_data_dir: Path, root_openviking_config
) -> AsyncGenerator[AsyncOpenViking, None]:
    """Create uninitialized OpenViking client (for testing initialization flow)"""
    await AsyncOpenViking.reset()

    client = AsyncOpenViking(path=str(test_data_dir))

    yield client

    try:
        await client.close()
    except Exception:
        pass
    finally:
        await AsyncOpenViking.reset()


@pytest_asyncio.fixture(scope="function")
async def client_with_resource_sync(
    client: AsyncOpenViking, sample_markdown_file: Path
) -> AsyncGenerator[tuple[AsyncOpenViking, str], None]:
    """Create client with resource (sync mode, wait for vectorization)"""
    result = await client.add_resource(
        path=str(sample_markdown_file), reason="Test resource", wait=True
    )
    uri = result.get("root_uri", "")

    yield client, uri


@pytest_asyncio.fixture(scope="function")
async def client_with_resource(
    client: AsyncOpenViking, sample_markdown_file: Path
) -> AsyncGenerator[tuple[AsyncOpenViking, str], None]:
    """Create client with resource (async mode, no wait for vectorization)"""
    result = await client.add_resource(path=str(sample_markdown_file), reason="Test resource")
    uri = result.get("root_uri", "")
    yield client, uri
