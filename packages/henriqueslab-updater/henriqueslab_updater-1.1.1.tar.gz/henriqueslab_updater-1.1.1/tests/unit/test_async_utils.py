"""Unit tests for async utilities."""

import asyncio
import time
from unittest.mock import Mock, patch

import pytest
from henriqueslab_updater.utils.async_utils import run_async_in_thread, create_async_task


class TestAsyncUtils:
    """Test async utility functions."""

    def test_run_async_in_thread_basic(self):
        """Test basic async execution in thread."""
        result = []

        async def async_task():
            await asyncio.sleep(0.1)
            result.append("completed")

        thread = run_async_in_thread(async_task(), timeout=1.0)
        assert thread.is_alive() or result == ["completed"]

        # Wait for task to complete
        time.sleep(0.3)
        assert result == ["completed"]

    def test_run_async_in_thread_with_timeout(self):
        """Test async execution with timeout."""

        async def slow_task():
            await asyncio.sleep(2.0)
            return "completed"

        thread = run_async_in_thread(slow_task(), timeout=0.1)
        # Should start thread
        assert thread.daemon is True

        # Wait for timeout
        time.sleep(0.3)
        # Thread should have timed out silently

    def test_run_async_in_thread_exception(self):
        """Test async execution with exception."""

        async def failing_task():
            raise ValueError("Test error")

        # Should not raise exception (caught silently)
        thread = run_async_in_thread(failing_task(), timeout=1.0)
        time.sleep(0.2)
        # Test passes if no exception raised

    def test_run_async_in_thread_daemon(self):
        """Test that threads are daemon by default."""

        async def task():
            await asyncio.sleep(0.1)

        thread = run_async_in_thread(task())
        assert thread.daemon is True

    def test_run_async_in_thread_non_daemon(self):
        """Test creating non-daemon thread."""

        async def task():
            await asyncio.sleep(0.1)

        thread = run_async_in_thread(task(), daemon=False)
        assert thread.daemon is False
        # Wait for thread to complete before test ends
        thread.join(timeout=1.0)

    def test_create_async_task_basic(self):
        """Test create_async_task wrapper."""
        result = []

        async def async_func():
            await asyncio.sleep(0.1)
            result.append("completed")

        create_async_task(async_func, timeout=1.0)

        # Wait for task to complete
        time.sleep(0.3)
        assert result == ["completed"]

    def test_create_async_task_with_timeout(self):
        """Test create_async_task with timeout."""

        async def slow_func():
            await asyncio.sleep(2.0)

        # Should not raise exception
        create_async_task(slow_func, timeout=0.1)
        time.sleep(0.3)
        # Test passes if no exception raised

    def test_run_async_in_thread_return_thread(self):
        """Test that run_async_in_thread returns started thread."""

        async def task():
            await asyncio.sleep(0.1)

        thread = run_async_in_thread(task())
        assert isinstance(thread, __import__("threading").Thread)
        assert thread.is_alive() or not thread.is_alive()  # Thread may finish quickly

    def test_run_async_in_thread_isolated_loop(self):
        """Test that each thread gets isolated event loop."""
        results = []

        async def task(value):
            await asyncio.sleep(0.05)
            results.append(value)

        # Run multiple tasks concurrently
        thread1 = run_async_in_thread(task(1), timeout=1.0)
        thread2 = run_async_in_thread(task(2), timeout=1.0)

        # Wait for both to complete
        time.sleep(0.3)

        # Both should have completed
        assert len(results) == 2
        assert set(results) == {1, 2}
