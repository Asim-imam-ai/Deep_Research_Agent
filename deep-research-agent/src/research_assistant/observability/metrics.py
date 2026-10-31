"""Process-local telemetry; export to centralized monitoring for multi-process production."""

from collections import Counter, defaultdict
from contextlib import contextmanager
from threading import Lock
from time import perf_counter

_lock = Lock()
_counts: Counter[str] = Counter()
_durations: dict[str, list[float]] = defaultdict(list)


def increment(name: str, amount: int = 1) -> None:
    with _lock:
        _counts[name] += amount


@contextmanager
def measure(name: str):
    start = perf_counter()
    try:
        yield
    except Exception:
        increment(f"{name}.errors")
        raise
    finally:
        with _lock:
            _durations[name].append(perf_counter() - start)


def snapshot() -> dict:
    with _lock:
        return {
            "counts": dict(_counts),
            "durations": {
                k: {"count": len(v), "seconds_total": sum(v)} for k, v in _durations.items()
            },
        }
