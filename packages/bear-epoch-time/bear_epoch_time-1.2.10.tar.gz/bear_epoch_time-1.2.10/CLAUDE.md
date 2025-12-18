# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About

This repository is maintained by Bear (also known as Chaz). Always refer to them as Bear, never as "the user" - they're a person who deserves to be called by their name!

## Project Overview

Bear Epoch Time is a Python library for handling epoch timestamps with timezone-aware operations. The core design philosophy:
- **EpochTimestamp is an int subclass** - Enables direct arithmetic while providing rich datetime operations
- **Milliseconds by default** - Most APIs work in milliseconds unless specified otherwise
- **UTC-first, timezone-aware** - All timestamps stored in UTC, timezone conversions handled explicitly
- **Fluent API** - Method chaining for time manipulations without datetime quirks

## Development Commands

### Testing
```bash
# Run tests with pytest
pytest

# Run tests across Python versions (3.11-3.14)
nox -s tests

# Run specific test file
pytest tests/test_epoch_timestamp.py
```

### Linting & Type Checking
```bash
# Run ruff linting (CI mode - checks only)
nox -s ruff_check

# Run ruff with auto-fix
nox -s ruff_fix

# Run pyright type checking
nox -s pyright

# All linting configured in config/ruff.toml
```

### Building
```bash
# Build package (uses hatchling + uv-dynamic-versioning)
python -m build

# Version is auto-generated from git tags via hatch_build.py
```

## Architecture

### Core Classes

**EpochTimestamp** (src/bear_epoch_time/epoch_timestamp.py:28)
- Inherits from `int` to allow direct arithmetic operations
- Stores epoch time in milliseconds or seconds (specified at initialization via `milliseconds` parameter)
- Key instance property: `self.milliseconds: bool` - Tracks whether the value is in ms or seconds
- Class-level configuration via `_repr_style`, `_datefmt`, `_timefmt`, `_fullfmt`, `_tz`
- Uses `@cached_property` for expensive operations like `_get_template_vars`
- Important: `is_default` property checks for zero value (placeholder)

**EpochTimestamp Format Interception** (src/bear_epoch_time/helpers.py:35)
- The `@fmt_parse` decorator intercepts format strings before processing
- Handles custom format codes like `%Do` (ordinal day: "1st", "2nd", "3rd")
- Applied to methods like `to_string()`, `date_str()`, `time_str()`, `from_dt_string()`

**TimeConverter** (src/bear_epoch_time/time_converter.py:28)
- Static utility class for time parsing and formatting
- `parse_to_seconds()` parses strings like "2d 3h 15m" using regex
- `format_seconds()` converts seconds to human-readable format
- Unit enum defines time units: M (month), d (day), h (hour), m (minute), s (second), ms (millisecond)

**TimeTools** (src/bear_epoch_time/time_tools.py:13)
- Instance-based utilities with configurable timezone and date format
- `get_day_range()` returns start/end of day as EpochTimestamp tuple
- Timezone-aware operations use the instance's configured timezone

**Timer Classes** (src/bear_epoch_time/timer.py)
- `TimerData`: Container for timing info with `start()`, `stop()`, `duration()` methods
- Context managers: `timer()` (sync) and `async_timer()` (async)
- Decorator factories: `create_timer()` and `create_async_timer()` for setting defaults
- Uses `perf_counter()` for high-resolution timing

### Key Patterns

**Millisecond/Second Conversion**
The `EpochTimestamp.op()` class method handles all ms/s conversions:
```python
# Multiply or divide by 1000 based on milliseconds flag
cls.op(v=timestamp, ms=True, op="mult")  # seconds -> milliseconds
cls.op(v=timestamp, ms=True, op="div")   # milliseconds -> seconds
```

**Timezone Handling**
- `TimeZoneHelper` (src/bear_epoch_time/tz.py) wraps pytz/zoneinfo
- Class uses `_local_tz_helper` as cached singleton via `tz_helper()` classmethod
- All timezone conversions go through this helper to ensure consistency

**Format String Magic**
The `fmt_convert` function and `@fmt_parse` decorator work together:
1. User provides format string (may contain `%Do`)
2. Decorator intercepts via `format_interception()`
3. Custom codes replaced with actual values
4. Result passed to `strftime()` for standard processing

## Python Version Support

- Requires Python 3.11+ (configured in pyproject.toml)
- Type hints use modern syntax: `list`, `dict`, `tuple` (not `List`, `Dict`, `Tuple`)
- Uses `|` for unions (not `Union`)
- Imports `Callable` from `collections.abc` (not `typing`)

## Testing Notes

- Tests use `pytest` with async support (`pytest-asyncio`)
- Test markers: `@pytest.mark.visual` for visual verification tests
- Conftest in tests/conftest.py provides shared fixtures
- Tests cover EpochTimestamp, TimeConverter, TimeTools, Timer classes

## Common Pitfalls

1. **Don't forget the `milliseconds` parameter** - When creating `EpochTimestamp`, the boolean flag determines interpretation
2. **Zero is a placeholder** - Check `is_default` property before operations that require valid timestamps
3. **UTC vs Local timezone** - Methods like `start_of_day()` accept optional `tz` parameter; without it, uses UTC
4. **Format string decorator** - Methods decorated with `@fmt_parse` support custom format codes
5. **Comparison operations** - EpochTimestamp overrides `__eq__`, `__lt__`, etc. to work with datetime, date, time, int, float

## Build System

- Uses `hatchling` as build backend with `uv-dynamic-versioning`
- Version derived from git tags (see hatch_build.py)
- Custom build hook generates src/bear_epoch_time/_internal/_version.py
- Lock file: uv.lock (uv package manager)

## Code Style Guidelines

### Comments Philosophy
Comments answer "why" or "watch out," never "what." Let clear naming and structure speak for themselves.

**Use comments ONLY for:**
- Library quirks/undocumented behavior
- Non-obvious business rules
- Future warnings
- Explaining necessary weirdness

**Prefer docstrings for:**
- Function/class explanations
- API documentation
- Parameter descriptions

**Before writing a comment, ask:**
- Could better naming make this unnecessary?
- Am I explaining WHAT (bad) or WHY (good)?

**Example of bad comment:**
```python
# Multiply by 1000
value = seconds * 1000
```

**Example of good comment:**
```python
# pytz requires localize() for naive datetimes, while zoneinfo uses replace()
if isinstance(timezone, PytzType):
    dt = timezone.localize(dt)
```
