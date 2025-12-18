#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

import contextlib
from typing import Callable, Any
from .profiler import QueryProfiler


def profile_queries(func: Callable):
    async def wrapper(*args, **kwargs):
        profiler = QueryProfiler()
        profiler.enable()

        try:
            result = await func(*args, **kwargs, profiler=profiler)
            return result
        finally:
            profiler.disable()

    return wrapper


@contextlib.contextmanager
def query_profiling():
    profiler = QueryProfiler()
    profiler.enable()
    try:
        yield profiler
    finally:
        profiler.disable()