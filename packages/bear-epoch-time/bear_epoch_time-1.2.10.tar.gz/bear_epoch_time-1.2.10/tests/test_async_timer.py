"""Tests for the async timer functionality in bear_epoch_time."""

from __future__ import annotations

import asyncio

from bear_epoch_time.timer import async_timer, create_async_timer

from .conftest import DummyConsole  # noqa: TC001


def test_async_timer_context_manager(dummy_console: DummyConsole) -> None:
    async def inner() -> None:
        """Inner function to test the async timer context manager."""
        async with async_timer(name="custom_async", console=dummy_console.print) as data:
            assert data.name == "custom_async"
            await asyncio.sleep(0)

    asyncio.run(inner())
    assert len(dummy_console.messages) == 1
    assert "custom_async" in dummy_console.messages[0]


def test_create_async_timer_decorator(dummy_console: DummyConsole) -> None:
    """Test the create_async_timer decorator."""

    @create_async_timer(console=dummy_console.print)
    async def decorated() -> str:
        """Decorated async function to test the timer."""
        await asyncio.sleep(0)
        return "done"

    result: str = asyncio.run(decorated())  # pyright: ignore[reportCallIssue]
    assert result == "done"
    assert len(dummy_console.messages) == 1
    assert "decorated" in dummy_console.messages[0]
