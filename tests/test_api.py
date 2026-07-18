"""
API endpoint tests (network-dependent: skip when service is down).
These require a running inference service and are marked to be skipped by default.
"""

import pytest

pytestmark = pytest.mark.integration


# ── Inference endpoint tests ─────────────────────────────────────────────


@pytest.mark.skip(reason="requires running service")
def test_inference_endpoint_reaches():
    """Verify the inference endpoint returns a response."""
    import httpx
    async def _check():
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("http://127.0.0.1:8001/v1/models")
            assert resp.status_code == 200
            data = resp.json()
            assert "data" in data
            assert len(data["data"]) > 0
    import asyncio
    asyncio.run(_check())


@pytest.mark.skip(reason="requires running service")
async def test_inference_completion():
    """Send a completion request and verify the response structure."""
    import httpx

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "http://127.0.0.1:8003/v1/completions",
            json={
                "model": "default",
                "prompt": "What is two plus two?",
                "max_tokens": 20,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "choices" in data
        assert len(data["choices"]) > 0