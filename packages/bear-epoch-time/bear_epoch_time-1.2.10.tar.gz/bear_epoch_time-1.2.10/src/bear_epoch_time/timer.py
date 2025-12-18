"""Tools related to timers and performance measurement."""

from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from enum import StrEnum
from functools import wraps
from time import perf_counter
from typing import TYPE_CHECKING, Any, Literal, ParamSpec, Self, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Generator
    from types import CoroutineType

T = TypeVar("T")
P = ParamSpec("P")


def create_timer(**kws) -> Callable[..., Callable[P, T]]:  # pyright: ignore[reportInvalidTypeVarUse]
    """A way to set defaults for a frequently used timer decorator."""

    def timer_decorator(func: Callable[P, T]) -> Callable[P, T]:
        """Decorator to time the execution of a function."""

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper to time the execution of a function."""
            defaults: dict[str, Any] = kws.copy()
            defaults["name"] = func.__name__
            with timer(**defaults):
                return func(*args, **kwargs)

        return wrapper

    return timer_decorator


def create_async_timer(**kws) -> Callable[..., Callable[P, CoroutineType[Any, Any, T]]]:  # pyright: ignore[reportInvalidTypeVarUse]
    """Set defaults for an async timer decorator."""

    def timer_decorator(func: Callable[P, CoroutineType[Any, Any, T]]) -> Callable[P, CoroutineType[Any, Any, T]]:
        """Decorator to time the execution of an async function."""

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Async wrapper to time the execution of an async function."""
            defaults: dict[str, Any] = kws.copy()
            defaults["name"] = func.__name__
            async with async_timer(**defaults):
                return await func(*args, **kwargs)

        return wrapper

    return timer_decorator


@contextmanager
def timer(**kwargs) -> Generator[TimerData]:
    """Context manager to time the execution of a block of code."""
    data: TimerData = kwargs.get("data") or TimerData(**kwargs)
    data.start()
    try:
        yield data
    finally:
        data.stop()


@asynccontextmanager
async def async_timer(**kwargs) -> AsyncGenerator[TimerData]:
    """Async context manager to time the execution of an async block of code."""
    data: TimerData = kwargs.get("data") or TimerData(**kwargs)
    data.start()
    try:
        yield data
    finally:
        data.stop()


TimeTypeValue = Literal["secs", "ms"]


class TimeType(StrEnum):
    """Enumeration for time types."""

    SECONDS = "secs"
    MILLISECONDS = "ms"


class TimerData:
    """Container for timing information."""

    def __init__(
        self,
        name: str = "",
        console: Callable[[str], None] | None = None,
        callback: Callable[[TimerData], None] | None = None,
        start: bool = False,
        time_type: TimeType | TimeTypeValue = TimeType.SECONDS,
    ) -> None:
        """Initialize the timer data.

        Args:
            name (str): The name of the timer, defaults to an empty string.
            console (Callable | None): A callable to print the timer output.
            callback (Callable | None): A callable to invoke when the timer stops.
            start (bool): Whether to start the timer immediately.
            time_type (TimeType): The type of time to report ("s" for seconds, "ms" for milliseconds), defaults to seconds.
        """
        self.name: str = name
        self._console: Callable[[str], None] | None = console
        self._callback: Callable[[TimerData], None] | None = callback
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.time_type: TimeType = TimeType(time_type)
        self._raw_elapsed_time: float = 0.0
        if start:
            self.start()

    @property
    def value(self) -> float:
        """Return the correct property based on the time type and if the timer has stopped."""
        return self.milliseconds if self.time_type == TimeType.MILLISECONDS else self.seconds

    @property
    def value_to_string(self) -> str:
        """Return the elapsed time as a formatted string."""
        string: str = f"{self.value:.6f} {self.time_type}"
        if not self.started:
            string = f"<{self.name}> Timer not started"
        return string

    @property
    def milliseconds(self) -> float:
        """Return the current elapsed time in milliseconds."""
        return self.duration() * 1000

    @property
    def seconds(self) -> float:
        """Return the current elapsed time in seconds."""
        return self.duration()

    @property
    def started(self) -> bool:
        """Check if the timer has been started."""
        return self.start_time > 0.0

    @property
    def stopped(self) -> bool:
        """Check if the timer has been stopped."""
        return self.end_time > 0.0

    def duration(self) -> float:
        """Calculate the elapsed time since the timer was started."""
        if not self.started:
            return 0.0
        if self.stopped:
            return self._raw_elapsed_time
        return perf_counter() - self.start_time

    def send_callback(self) -> Self:
        """Invoke the callback if one was provided."""
        if self._callback is not None:
            self._callback(self)
        return self

    def print_to_console(self, msg: str | None = None, exception: Exception | None = None, err: bool = False) -> Self:
        """Print the current elapsed time without stopping the timer."""
        if self._console is not None and callable(self._console):
            if not err and msg is None:
                self._console(f"<{self.name}> Elapsed time: {self.value_to_string}")
            elif msg is not None and err and exception is not None:
                self._console(f"<{self.name}> {msg}, Error: {exception}")
        return self

    def start(self) -> Self:
        """Record the starting time using ``perf_counter``."""
        self.start_time = perf_counter()
        return self

    def stop(self) -> Self:
        """Record the ending time using ``perf_counter`` and calculate elapsed time."""
        if not self.started:
            raise RuntimeError("Timer has not been started.")
        self.end_time = perf_counter()
        self._raw_elapsed_time = self.end_time - self.start_time
        try:
            self.send_callback()
        except Exception as err:
            self.print_to_console("Callback error", exception=err, err=True)
        try:
            self.print_to_console()
        except Exception as err:
            self.print_to_console("Console print error", exception=err, err=True)

        return self

    def reset(self) -> Self:
        """Reset the timer to its initial state."""
        self.start_time = 0.0
        self.end_time = 0.0
        self._raw_elapsed_time = 0.0
        return self


__all__ = ["TimerData", "timer"]
