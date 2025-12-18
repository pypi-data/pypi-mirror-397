"""Robust subprocess management for async workflows."""

from __future__ import annotations

import asyncio
import os
import signal
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass
class SubprocessResult:
    """Result of a managed subprocess."""

    returncode: int
    stdout: bytes
    stderr: bytes


class SubprocessManager:
    """Helper for running subprocesses with consistent timeout/cleanup."""

    @staticmethod
    async def run(
        cmd: Iterable[str],
        *,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        timeout: float | None = None,
        stdin_data: bytes | None = None,
        stdout_callback: Callable[[bytes], None] | None = None,
        stderr_callback: Callable[[bytes], None] | None = None,
    ) -> SubprocessResult:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if stdin_data else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env or os.environ.copy(),
        )

        async def _pump_stream(stream, sink: bytearray, callback):
            """Read from stream, optionally emitting to callback."""
            while True:
                chunk = await stream.readline()
                if not chunk:
                    break
                sink.extend(chunk)
                if callback:
                    try:
                        callback(chunk)
                    except Exception:
                        # Don't break subprocess handling if callback fails
                        pass

        try:
            if stdout_callback or stderr_callback:
                if stdin_data and proc.stdin:
                    proc.stdin.write(stdin_data)
                    await proc.stdin.drain()
                    proc.stdin.close()

                stdout_sink: bytearray = bytearray()
                stderr_sink: bytearray = bytearray()

                tasks = []
                if proc.stdout:
                    tasks.append(asyncio.create_task(_pump_stream(proc.stdout, stdout_sink, stdout_callback)))
                if proc.stderr:
                    tasks.append(asyncio.create_task(_pump_stream(proc.stderr, stderr_sink, stderr_callback)))
                tasks.append(asyncio.create_task(proc.wait()))

                await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
                stdout, stderr = bytes(stdout_sink), bytes(stderr_sink)
            else:
                stdout, stderr = await asyncio.wait_for(proc.communicate(input=stdin_data), timeout=timeout)
        except asyncio.TimeoutError:
            SubprocessManager._terminate(proc)
            raise
        except asyncio.CancelledError:
            SubprocessManager._terminate(proc)
            raise

        return SubprocessResult(proc.returncode or 0, stdout, stderr)

    @staticmethod
    def _terminate(proc: asyncio.subprocess.Process) -> None:
        try:
            if proc.returncode is None:
                proc.send_signal(signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            # Give it a moment then kill if needed
            try:
                proc.kill()
            except ProcessLookupError:
                pass
        finally:
            # Ensure streams are closed
            try:
                if proc.stdin:
                    proc.stdin.close()
            except Exception:
                pass
