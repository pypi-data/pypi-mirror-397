"""Async utilities for background update checking."""

import asyncio
import threading
from typing import Any, Callable, Coroutine, Optional


def run_async_in_thread(
    coro: Coroutine[Any, Any, Any],
    timeout: float = 30.0,
    daemon: bool = True,
) -> threading.Thread:
    """Run an async coroutine in a background thread with a new event loop.

    This function creates an isolated event loop in a new thread, preventing
    "event loop already running" errors. The thread is daemonic by default,
    meaning it won't prevent the main program from exiting.

    Args:
        coro: The coroutine to run
        timeout: Maximum time to allow the coroutine to run (default: 30 seconds)
        daemon: Whether the thread should be daemonic (default: True)

    Returns:
        The thread object (already started)
    """

    def _run_in_thread() -> None:
        """Target function for the thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
        except asyncio.TimeoutError:
            # Silent timeout - don't disrupt main application
            pass
        except Exception:
            # Silent failure - update check errors should never disrupt the app
            pass
        finally:
            loop.close()

    thread = threading.Thread(target=_run_in_thread, daemon=daemon)
    thread.start()
    return thread


def create_async_task(
    func: Callable[[], Coroutine[Any, Any, Any]],
    timeout: float = 30.0,
) -> None:
    """Create and run an async task in a background thread.

    This is a convenience wrapper around run_async_in_thread that creates
    the coroutine from a callable.

    Args:
        func: Callable that returns a coroutine
        timeout: Maximum time to allow the task to run
    """
    coro = func()
    run_async_in_thread(coro, timeout=timeout)
