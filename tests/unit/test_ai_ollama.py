import json
import logging
from collections.abc import AsyncIterator, Callable
from typing import Any

import httpx
import pytest

from app.adapters.ai_ollama import OllamaAi, _ThinkFilter
from app.core.config import Settings, get_settings
from app.ports.ai import ProviderError, ProviderTimeout


def _ai(handler: Callable[[httpx.Request], httpx.Response], **overrides: Any) -> OllamaAi:
    settings: Settings = get_settings().model_copy(
        update={"embedding_dim": 3, "embed_batch_size": 32, **overrides}
    )
    return OllamaAi(settings, transport=httpx.MockTransport(handler))


def _ndjson(*events: dict[str, Any]) -> bytes:
    return "".join(json.dumps(e) + "\n" for e in events).encode()


def _chunks(*texts: str) -> bytes:
    events: list[dict[str, Any]] = [{"message": {"role": "assistant", "content": t}, "done": False}
                                    for t in texts]  # fmt: skip
    events.append({"message": {"content": ""}, "done": True})
    return _ndjson(*events)


async def test_embed_batches_and_order() -> None:
    requests: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        requests.append(body)
        return httpx.Response(200, json={"embeddings": [[float(t), 0.0, 0.0] for t in body["input"]]})

    vectors = await _ai(handler).embed([str(i) for i in range(40)])
    assert len(requests) == 2 and [len(r["input"]) for r in requests] == [32, 8]
    assert [v[0] for v in vectors] == [float(i) for i in range(40)]


async def test_embed_request_shape_has_no_identifiers() -> None:
    seen: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.content)
        return httpx.Response(200, json={"embeddings": [[0.1, 0.2, 0.3]]})

    ai = _ai(handler)
    await ai.embed(["noi dung"])
    assert set(json.loads(seen[0])) == {"model", "input"}
    assert json.loads(seen[0])["model"] == "qwen3-embedding:0.6b"
    assert b"@" not in seen[0]


@pytest.mark.parametrize("status", [401, 403, 429, 500, 503])
async def test_http_errors_mapped(status: int) -> None:
    ai = _ai(lambda request: httpx.Response(status, text="loi"))
    with pytest.raises(ProviderError):
        await ai.embed(["a"])
    with pytest.raises(ProviderError):
        [t async for t in ai.generate("s", "u")]


async def test_network_error_and_timeout_mapped() -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    def slow(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow")

    with pytest.raises(ProviderError):
        await _ai(refuse).embed(["a"])
    with pytest.raises(ProviderTimeout):
        await _ai(slow).embed(["a"])
    with pytest.raises(ProviderTimeout):
        [t async for t in _ai(slow).generate("s", "u")]


async def test_embed_bad_response_and_count_mismatch() -> None:
    with pytest.raises(ProviderError):
        await _ai(lambda r: httpx.Response(200, json={"oops": 1})).embed(["a"])
    with pytest.raises(ProviderError):
        await _ai(lambda r: httpx.Response(200, json={"embeddings": []})).embed(["a"])


async def test_embed_dimension_self_check() -> None:
    ok = _ai(lambda r: httpx.Response(200, json={"embeddings": [[0.1, 0.2, 0.3]]}))
    await ok.self_check()
    bad = _ai(lambda r: httpx.Response(200, json={"embeddings": [[0.1] * 10]}))
    with pytest.raises(RuntimeError, match="3"):
        await bad.self_check()


async def test_generate_streams() -> None:
    ai = _ai(lambda r: httpx.Response(200, content=_chunks("Xin ", "chào ", "[c1].")))
    assert [t async for t in ai.generate("hệ thống", "câu hỏi")] == ["Xin ", "chào ", "[c1]."]


async def test_generate_request_body_shape() -> None:
    seen: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return httpx.Response(200, content=_chunks("ok"))

    [t async for t in _ai(handler).generate("SYS", "USR")]
    body = seen[0]
    assert body["model"] == "qwen3:1.7b" and body["stream"] is True and body["think"] is False
    assert body["options"] == {"temperature": 0.1, "num_predict": 800}
    assert [m["role"] for m in body["messages"]] == ["system", "user"]


async def test_error_mid_stream() -> None:
    async def broken() -> AsyncIterator[bytes]:
        yield _chunks("Xin ")[: len(_chunks("Xin ")) - len(_ndjson({"message": {"content": ""}, "done": True}))]
        raise httpx.ReadError("connection reset")

    ai = _ai(lambda r: httpx.Response(200, content=broken()))
    got: list[str] = []
    with pytest.raises(ProviderError):
        async for token in ai.generate("s", "u"):
            got.append(token)
    assert got == ["Xin "]


async def test_error_event_in_stream() -> None:
    ai = _ai(lambda r: httpx.Response(200, content=_ndjson({"error": "model not found"})))
    with pytest.raises(ProviderError):
        [t async for t in ai.generate("s", "u")]


async def test_aclose_closes_http() -> None:
    responses: list[httpx.Response] = []

    async def endless() -> AsyncIterator[bytes]:
        for i in range(1000):
            yield _ndjson({"message": {"content": f"t{i} "}, "done": False})

    def handler(request: httpx.Request) -> httpx.Response:
        response = httpx.Response(200, content=endless())
        responses.append(response)
        return response

    stream = _ai(handler).generate("s", "u")
    assert await anext(stream) == "t0 " and await anext(stream) == "t1 "
    await stream.aclose()
    assert responses[0].is_closed


async def test_think_blocks_removed_from_stream() -> None:
    ai = _ai(lambda r: httpx.Response(200, content=_chunks("<thi", "nk>suy luận", " ẩn</th", "ink>\nTrả lời ", "[c1].")))
    assert "".join([t async for t in ai.generate("s", "u")]) == "Trả lời [c1]."


def test_think_filter_handles_plain_text_and_partial_tag() -> None:
    f = _ThinkFilter()
    assert f.feed("a < b ") + f.feed("và <") + f.feed("x>") + f.flush() == "a < b và <x>"


async def test_logs_never_contain_text(caplog: pytest.LogCaptureFixture) -> None:
    ai = _ai(lambda r: httpx.Response(401, text="BÍ_MẬT"))
    with caplog.at_level(logging.DEBUG), pytest.raises(ProviderError):
        await ai.embed(["BÍ_MẬT_NGƯỜI_DÙNG"])
    assert "BÍ_MẬT" not in caplog.text
    assert "ai_auth_failed" in caplog.text
