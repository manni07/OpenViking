from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import vikingbot.providers.vlm_adapter as vlm_adapter
from vikingbot.providers.vlm_adapter import VLMProviderAdapter
from volcenginesdkarkruntime._exceptions import ArkRateLimitError

import openviking.utils.model_retry as model_retry
from openviking.models.vlm.backends.openai_vlm import OpenAIVLM
from openviking.utils.model_retry import is_retryable_rate_limit_error


class _DisabledLangfuse:
    enabled = False
    _client = None


class _FakeVLM:
    def __init__(self, failures: list[Exception], result: str = "ok"):
        self.failures = list(failures)
        self.result = result
        self.calls = 0

    async def get_completion_async(self, **_kwargs):
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return self.result


class _FakeVolcEngineFailoverVLM(_FakeVLM):
    provider = "volcengine"
    model = "primary-model"
    thinking = False


class _AsyncChunks:
    def __init__(self, chunks):
        self._chunks = chunks

    def __aiter__(self):
        return self._iter()

    async def _iter(self):
        for chunk in self._chunks:
            yield chunk


class _FakeStreamingCompletions:
    def __init__(self, failures: list[Exception], chunks):
        self.failures = list(failures)
        self.chunks = chunks
        self.calls = 0

    async def create(self, **_kwargs):
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return _AsyncChunks(self.chunks)


class _FakeStreamingVLM:
    provider = "volcengine"
    model = "test-model"
    thinking = False

    def __init__(self, completions: _FakeStreamingCompletions):
        self._client = SimpleNamespace(
            chat=SimpleNamespace(completions=completions),
        )

    def get_async_client(self):
        return self._client


@pytest.mark.asyncio
async def test_chat_retries_rate_limit_until_success(monkeypatch):
    sleep_delays: list[float] = []

    async def _sleep(delay: float):
        sleep_delays.append(delay)

    monkeypatch.setattr(vlm_adapter, "rate_limit_retry_delay", lambda attempt: attempt)
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", _sleep)

    fake_vlm = _FakeVLM(
        [
            RuntimeError("Error code: 429 - ModelAccountTpmRateLimitExceeded"),
            RuntimeError("TooManyRequests: rate limit"),
        ],
        result="done",
    )
    adapter = VLMProviderAdapter(fake_vlm, "test-model", langfuse_client=_DisabledLangfuse())

    response = await adapter.chat(messages=[{"role": "user", "content": "hello"}])

    assert response.content == "done"
    assert response.finish_reason == "stop"
    assert fake_vlm.calls == 3
    assert sleep_delays == [1, 2]


@pytest.mark.asyncio
async def test_chat_does_not_retry_errors_without_rate_limit_markers(monkeypatch):
    async def _sleep(_delay: float):
        raise AssertionError("non-retryable errors must not sleep/retry")

    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", _sleep)

    fake_vlm = _FakeVLM([RuntimeError("AuthenticationError Unauthorized")])
    adapter = VLMProviderAdapter(fake_vlm, "test-model", langfuse_client=_DisabledLangfuse())

    response = await adapter.chat(messages=[{"role": "user", "content": "hello"}])

    assert response.finish_reason == "error"
    assert "AuthenticationError" in response.content
    assert fake_vlm.calls == 1


@pytest.mark.asyncio
async def test_chat_accepts_string_response_from_openai_backend_with_tools(monkeypatch):
    async def create(**_kwargs):
        return "plain string response"

    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
    )
    vlm = OpenAIVLM({"provider": "openai", "model": "gpt-5.6-terra"})
    monkeypatch.setattr(vlm, "get_async_client", lambda: client)
    adapter = VLMProviderAdapter(vlm, "gpt-5.6-terra", langfuse_client=_DisabledLangfuse())

    response = await adapter.chat(
        messages=[{"role": "user", "content": "hello"}],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ],
    )

    assert response.content == "plain string response"
    assert response.tool_calls == []
    assert response.finish_reason == "stop"


@pytest.mark.asyncio
async def test_chat_without_tools_preserves_usage_from_openai_backend(monkeypatch):
    raw_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="plain response", tool_calls=None),
                finish_reason="stop",
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=13,
            completion_tokens=5,
            total_tokens=18,
            prompt_tokens_details=None,
            completion_tokens_details=None,
        ),
    )

    async def create(**kwargs):
        assert "tools" not in kwargs
        return raw_response

    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
    )
    vlm = OpenAIVLM({"provider": "openai", "model": "gpt-5.6-terra"})
    monkeypatch.setattr(vlm, "get_async_client", lambda: client)
    adapter = VLMProviderAdapter(vlm, "gpt-5.6-terra", langfuse_client=_DisabledLangfuse())

    response = await adapter.chat(messages=[{"role": "user", "content": "hello"}])

    assert response.content == "plain response"
    assert response.tool_calls == []
    assert response.finish_reason == "stop"
    assert response.usage == {
        "prompt_tokens": 13,
        "completion_tokens": 5,
        "total_tokens": 18,
        "prompt_tokens_details": None,
    }


@pytest.mark.asyncio
async def test_chat_stream_retries_rate_limit_until_success(monkeypatch):
    sleep_delays: list[float] = []

    async def _sleep(delay: float):
        sleep_delays.append(delay)

    monkeypatch.setattr(vlm_adapter, "rate_limit_retry_delay", lambda attempt: attempt)
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", _sleep)

    chunk = SimpleNamespace(
        usage=None,
        choices=[
            SimpleNamespace(
                finish_reason=None,
                delta=SimpleNamespace(content="streamed", reasoning_content=None),
            )
        ],
    )
    completions = _FakeStreamingCompletions(
        [RuntimeError("Error code: 429 - ModelAccountTpmRateLimitExceeded")],
        [chunk],
    )
    adapter = VLMProviderAdapter(
        _FakeStreamingVLM(completions),
        "test-model",
        langfuse_client=_DisabledLangfuse(),
    )

    events = [
        event
        async for event in adapter.chat_stream(
            messages=[{"role": "user", "content": "hello"}],
        )
    ]

    assert completions.calls == 2
    assert sleep_delays == [1]
    assert [event.type for event in events] == ["content_delta", "response"]
    assert events[0].content == "streamed"
    assert events[1].response.content == "streamed"
    assert events[1].response.finish_reason == "stop"


@pytest.mark.asyncio
async def test_chat_stream_routes_failover_wrapper_through_completion_api():
    fake_vlm = _FakeVolcEngineFailoverVLM([], result="fallback-safe")
    adapter = VLMProviderAdapter(
        fake_vlm,
        "primary-model",
        langfuse_client=_DisabledLangfuse(),
    )

    events = [
        event
        async for event in adapter.chat_stream(
            messages=[{"role": "user", "content": "hello"}],
        )
    ]

    assert fake_vlm.calls == 1
    assert [event.type for event in events] == ["response"]
    assert events[0].response.content == "fallback-safe"


def test_rate_limit_classifier_handles_target_error():
    assert is_retryable_rate_limit_error(
        RuntimeError("Error code: 429 - ModelAccountTpmRateLimitExceeded")
    )
    assert is_retryable_rate_limit_error(
        RuntimeError(
            "Error code: 429 - {'error': {'code': 'ModelAccountTpmRateLimitExceeded', "
            "'message': 'TPM (Tokens Per Minute) limit of the model doubao-seed-2-0-pro "
            "is exceeded. Please try again later Request id: "
            "0217817720969006061aa40146dbf4d117b0497e84060d7ac9102', "
            "'param': '', 'type': 'TooManyRequests'}}, request_id: "
            "202606181641366ORRzhOSo5se81lzpolL"
        )
    )
    assert is_retryable_rate_limit_error(RuntimeError("Error code: 429 - busy"))
    assert not is_retryable_rate_limit_error(RuntimeError("Error code: 401 Unauthorized"))
    assert not is_retryable_rate_limit_error(RuntimeError("trace_id=abc429def unrelated"))
    assert not is_retryable_rate_limit_error(RuntimeError("request_id=abc429def unrelated"))


def test_rate_limit_classifier_handles_structured_sdk_errors():
    request = httpx.Request("POST", "https://example.test")
    response = httpx.Response(429, request=request)
    exc = ArkRateLimitError(
        "Error code: 429 - rate limited",
        response=response,
        body={
            "code": "ModelAccountTpmRateLimitExceeded",
            "type": "TooManyRequests",
            "message": "TPM limit exceeded",
        },
        request_id="0217817720969006061aa40146dbf4d117b0497e84060d7ac9102",
    )

    assert is_retryable_rate_limit_error(exc)


def _mark_non_retryable(error: Exception) -> Exception:
    mark = getattr(model_retry, "mark_vlm_error_non_retryable", None)
    assert callable(mark), "model_retry must define mark_vlm_error_non_retryable"
    assert mark(error) is error
    return error


def _is_marked(error: Exception) -> bool:
    check = getattr(model_retry, "is_vlm_error_non_retryable", None)
    assert callable(check), "model_retry must define is_vlm_error_non_retryable"
    return check(error)


@pytest.mark.asyncio
async def test_chat_stops_marked_error_before_rate_limit_classifier_or_replay(monkeypatch):
    error = _mark_non_retryable(RuntimeError("429 after partial stream"))
    fake_vlm = _FakeVLM([error])
    classifier = MagicMock(return_value=True)
    sleep = AsyncMock()
    monkeypatch.setattr(vlm_adapter, "is_retryable_rate_limit_error", classifier)
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", sleep)
    adapter = VLMProviderAdapter(fake_vlm, "test-model", langfuse_client=_DisabledLangfuse())

    response = await adapter.chat(messages=[{"role": "user", "content": "hello"}])

    assert response.finish_reason == "error"
    assert fake_vlm.calls == 1
    classifier.assert_not_called()
    sleep.assert_not_called()


class _FailAfterEvents:
    def __init__(self, events, error: Exception):
        self._events = list(events)
        self._error = error

    def __aiter__(self):
        return self._iterate()

    async def _iterate(self):
        for event in self._events:
            yield event
        raise self._error


class _OneShotStreamingCompletions:
    def __init__(self, response):
        self.response = response
        self.calls = 0

    async def create(self, **_kwargs):
        self.calls += 1
        return self.response


def _native_event(shape: str):
    if shape == "empty":
        return SimpleNamespace(usage=None, choices=[])
    if shape == "usage-only":
        return SimpleNamespace(
            usage=SimpleNamespace(
                prompt_tokens=1,
                completion_tokens=0,
                total_tokens=1,
            ),
            choices=[],
        )
    delta = SimpleNamespace(content=None, reasoning_content=None, tool_calls=[])
    if shape == "reasoning-only":
        delta.reasoning_content = "reasoning"
    elif shape == "content":
        delta.content = "visible"
    elif shape == "tool-only":
        delta.tool_calls = [
            SimpleNamespace(
                index=0,
                id="call-1",
                function=SimpleNamespace(name="lookup", arguments="{}"),
            )
        ]
    else:
        raise AssertionError(f"unsupported shape: {shape}")
    return SimpleNamespace(
        usage=None,
        choices=[SimpleNamespace(finish_reason=None, delta=delta)],
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "shape",
    ["empty", "usage-only", "reasoning-only", "content", "tool-only"],
)
async def test_native_stream_marks_every_read_event_before_shape_handling(
    monkeypatch,
    shape,
):
    error = RuntimeError(f"429 after {shape} event")
    completions = _OneShotStreamingCompletions(_FailAfterEvents([_native_event(shape)], error))
    classifier = MagicMock(return_value=False)
    sleep = AsyncMock()
    monkeypatch.setattr(vlm_adapter, "is_retryable_rate_limit_error", classifier)
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", sleep)
    adapter = VLMProviderAdapter(
        _FakeStreamingVLM(completions),
        "test-model",
        langfuse_client=_DisabledLangfuse(),
    )

    events = [
        event
        async for event in adapter.chat_stream(
            messages=[{"role": "user", "content": "hello"}],
        )
    ]

    assert _is_marked(error) is True
    assert completions.calls == 1
    classifier.assert_not_called()
    sleep.assert_not_called()
    assert events[-1].type == "response"
    assert events[-1].response.finish_reason == "error"


class _ExplodingEvent:
    def __init__(self, error: Exception):
        self._error = error

    @property
    def usage(self):
        raise self._error


@pytest.mark.asyncio
async def test_native_stream_marks_progress_before_first_property_access(monkeypatch):
    error = RuntimeError("SENTINEL-FIRST-PROPERTY")
    completions = _OneShotStreamingCompletions(_AsyncChunks([_ExplodingEvent(error)]))
    classifier = MagicMock(return_value=False)
    sleep = AsyncMock()
    monkeypatch.setattr(vlm_adapter, "is_retryable_rate_limit_error", classifier)
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", sleep)
    adapter = VLMProviderAdapter(
        _FakeStreamingVLM(completions),
        "test-model",
        langfuse_client=_DisabledLangfuse(),
    )

    events = [
        event
        async for event in adapter.chat_stream(
            messages=[{"role": "user", "content": "hello"}],
        )
    ]

    assert _is_marked(error) is True
    assert completions.calls == 1
    classifier.assert_not_called()
    sleep.assert_not_called()
    assert events[-1].response.finish_reason == "error"


class _SentinelError(RuntimeError):
    def __init__(self, sentinel):
        super().__init__(f"{sentinel}-MESSAGE", f"{sentinel}-ARGS")
        self.opaque_payload = {"credential": f"{sentinel}-OPAQUE"}
        self.__cause__ = RuntimeError(f"{sentinel}-CAUSE")
        self.__context__ = RuntimeError(f"{sentinel}-CONTEXT")

    def __repr__(self):
        return f"SentinelError({self.args[0]}-REPR)"


class _MarkerAssignmentRejectingSentinelError(_SentinelError):
    def __setattr__(self, name, value):
        if name == "_openviking_vlm_non_retryable":
            raise RuntimeError("instance marker assignment denied")
        super().__setattr__(name, value)


_REDACTED_RESPONSE = "VLM response interrupted after partial output."
_REDACTED_LOG = "VLM adapter stopped a non-retryable partial stream."
_REDACTED_CATEGORY = "partial_stream_non_retryable"


class _CaptureObservation:
    def __init__(self, calls):
        self.calls = calls

    def update(self, **kwargs):
        self.calls.append(("update", kwargs))

    def end(self):
        self.calls.append(("end", {}))


class _CaptureLangfuse:
    enabled = True

    def __init__(self):
        self._client = self
        self.calls = []

    def start_observation(self, **kwargs):
        self.calls.append(("start", kwargs))
        return _CaptureObservation(self.calls)

    def register_generation(self, *_args, **kwargs):
        self.calls.append(("register", kwargs))

    def update_generation_metadata(self, _response_id, metadata):
        return metadata

    def flush(self):
        self.calls.append(("flush", {}))


@pytest.mark.asyncio
async def test_marked_chat_error_redacts_response_logger_and_langfuse_payload(monkeypatch):
    responses = []
    captures = []
    logger = MagicMock()
    classifier = MagicMock(return_value=True)
    sleep = AsyncMock()
    monkeypatch.setattr(vlm_adapter, "logger", logger)
    monkeypatch.setattr(vlm_adapter, "is_retryable_rate_limit_error", classifier)
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", sleep)

    forbidden = []
    for sentinel in ("SENTINEL-MESSAGE-A", "SENTINEL-OPAQUE-B"):
        langfuse = _CaptureLangfuse()
        error = _mark_non_retryable(_SentinelError(sentinel))
        forbidden.extend(
            (
                str(error),
                repr(error),
                repr(error.opaque_payload),
                str(error.__cause__),
                str(error.__context__),
            )
        )
        adapter = VLMProviderAdapter(_FakeVLM([error]), "test-model", langfuse)
        responses.append(await adapter.chat([{"role": "user", "content": "safe"}]))
        captures.append(langfuse.calls)

    assert [item.content for item in responses] == [_REDACTED_RESPONSE] * 2
    assert [item.finish_reason for item in responses] == ["error", "error"]
    assert [item.args for item in logger.mock_calls] == [(_REDACTED_LOG,)] * 2
    updates = [[payload for name, payload in calls if name == "update"] for calls in captures]
    assert (
        updates == [[{"output": _REDACTED_RESPONSE, "metadata": {"error": _REDACTED_CATEGORY}}]] * 2
    )
    captured = repr((responses, logger.mock_calls, captures))
    assert all(value not in captured for value in forbidden)
    classifier.assert_not_called()
    sleep.assert_not_called()


@pytest.mark.asyncio
async def test_marked_native_stream_error_redacts_terminal_response_and_all_sinks(monkeypatch):
    terminal_contents = []
    captures = []
    logger = MagicMock()
    classifier = MagicMock(return_value=True)
    sleep = AsyncMock()
    monkeypatch.setattr(vlm_adapter, "logger", logger)
    monkeypatch.setattr(vlm_adapter, "is_retryable_rate_limit_error", classifier)
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", sleep)

    forbidden = []
    for sentinel in ("SENTINEL-STREAM-A", "SENTINEL-STREAM-B"):
        error = _mark_non_retryable(_SentinelError(sentinel))
        forbidden.extend(
            (
                str(error),
                repr(error),
                repr(error.opaque_payload),
                str(error.__cause__),
                str(error.__context__),
            )
        )
        completions = _OneShotStreamingCompletions(
            _FailAfterEvents([_native_event("content")], error)
        )
        langfuse = _CaptureLangfuse()
        adapter = VLMProviderAdapter(_FakeStreamingVLM(completions), "test-model", langfuse)
        events = [
            event async for event in adapter.chat_stream([{"role": "user", "content": "safe"}])
        ]
        terminal = events[-1].response
        assert terminal.finish_reason == "error"
        terminal_contents.append(terminal.content)
        captures.append(langfuse.calls)
        captured = repr((events, logger.mock_calls, langfuse.calls))
        assert all(value not in captured for value in forbidden)

    assert terminal_contents == [_REDACTED_RESPONSE] * 2
    assert [item.args for item in logger.mock_calls] == [(_REDACTED_LOG,)] * 2
    updates = [[payload for name, payload in calls if name == "update"] for calls in captures]
    assert (
        updates == [[{"output": _REDACTED_RESPONSE, "metadata": {"error": _REDACTED_CATEGORY}}]] * 2
    )
    classifier.assert_not_called()
    sleep.assert_not_called()


@pytest.mark.asyncio
async def test_marked_native_stream_langfuse_allows_only_response_id_metadata(monkeypatch):
    response_id = "response-id-only"
    monkeypatch.setattr(vlm_adapter, "get_current_response_id", lambda: response_id)
    monkeypatch.setattr(vlm_adapter, "logger", MagicMock())
    monkeypatch.setattr(vlm_adapter, "is_retryable_rate_limit_error", MagicMock(return_value=True))
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", AsyncMock())

    error = _mark_non_retryable(_SentinelError("SENTINEL-STREAM-RESPONSE-ID"))
    completions = _OneShotStreamingCompletions(_FailAfterEvents([_native_event("content")], error))
    langfuse = _CaptureLangfuse()
    adapter = VLMProviderAdapter(_FakeStreamingVLM(completions), "test-model", langfuse)

    events = [event async for event in adapter.chat_stream([{"role": "user", "content": "safe"}])]

    assert events[-1].response.content == _REDACTED_RESPONSE
    updates = [payload for name, payload in langfuse.calls if name == "update"]
    assert updates == [
        {
            "output": _REDACTED_RESPONSE,
            "metadata": {
                "error": _REDACTED_CATEGORY,
                "response_id": response_id,
            },
        }
    ]


@pytest.mark.asyncio
async def test_native_stream_wraps_assignment_rejection_without_replay_or_secret_leak(monkeypatch):
    sentinel = "SENTINEL-REJECTING-MARKER"
    error = _MarkerAssignmentRejectingSentinelError(sentinel)
    completions = _OneShotStreamingCompletions(_FailAfterEvents([_native_event("content")], error))
    logger = MagicMock()
    classifier = MagicMock(return_value=True)
    sleep = AsyncMock()
    langfuse = _CaptureLangfuse()
    monkeypatch.setattr(vlm_adapter, "logger", logger)
    monkeypatch.setattr(vlm_adapter, "is_retryable_rate_limit_error", classifier)
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", sleep)
    adapter = VLMProviderAdapter(_FakeStreamingVLM(completions), "test-model", langfuse)

    events = [event async for event in adapter.chat_stream([{"role": "user", "content": "safe"}])]

    assert completions.calls == 1
    classifier.assert_not_called()
    sleep.assert_not_called()
    assert events[-1].response.content == _REDACTED_RESPONSE
    assert [item.args for item in logger.mock_calls] == [(_REDACTED_LOG,)]
    updates = [payload for name, payload in langfuse.calls if name == "update"]
    assert updates == [{"output": _REDACTED_RESPONSE, "metadata": {"error": _REDACTED_CATEGORY}}]
    assert sentinel not in repr((events, logger.mock_calls, langfuse.calls))


@pytest.mark.asyncio
async def test_unmarked_chat_error_retains_legacy_visible_error_detail(monkeypatch):
    sentinel = "SENTINEL-UNMARKED-POSITIVE-CONTROL"
    monkeypatch.setattr(vlm_adapter.asyncio, "sleep", AsyncMock())
    adapter = VLMProviderAdapter(
        _FakeVLM([_SentinelError(sentinel)]),
        "test-model",
        _DisabledLangfuse(),
    )
    response = await adapter.chat([{"role": "user", "content": "safe"}])
    assert response.finish_reason == "error"
    assert sentinel in response.content
