"""Subprocess helpers for chapter verification tests."""

import subprocess
import time
import threading
import urllib.request
import urllib.error
from contextlib import contextmanager
from pathlib import Path


def find_repo_root():
    """Walk up from this file to find the directory with pyproject.toml."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not find repo root")


def run(cmd, *, cwd=None, timeout=30, **kwargs):
    """Run a command and return stdout. Raises on non-zero exit."""
    result = subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=timeout,
        **kwargs,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            cmd,
            output=result.stdout,
            stderr=result.stderr,
        )
    return result.stdout


@contextmanager
def background(cmd, ready_pattern, *, cwd=None, timeout=15):
    """Start a process in the background, wait for ready_pattern in output.

    Yields the Popen object once ready. Kills the process on exit.
    """
    proc = subprocess.Popen(
        cmd,
        shell=isinstance(cmd, str),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd,
    )

    output_lines = []

    def _reader():
        for line in proc.stdout:
            output_lines.append(line)

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()

    deadline = time.monotonic() + timeout
    try:
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                collected = "".join(output_lines)
                raise RuntimeError(
                    f"Process exited early (rc={proc.returncode}):\n{collected}"
                )
            if any(ready_pattern in line for line in output_lines):
                break
            time.sleep(0.1)
        else:
            collected = "".join(output_lines)
            proc.kill()
            raise TimeoutError(
                f"Ready pattern {ready_pattern!r} not seen after {timeout}s.\n"
                f"Output so far:\n{collected}"
            )
        yield proc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def wait_for_http(url, *, timeout=10):
    """Poll a URL until it returns 200. Raises on timeout."""
    deadline = time.monotonic() + timeout
    last_err = None
    while time.monotonic() < deadline:
        try:
            resp = urllib.request.urlopen(url)
            if resp.status == 200:
                return resp.read()
        except (urllib.error.URLError, ConnectionError) as e:
            last_err = e
        time.sleep(0.2)
    raise TimeoutError(f"{url} not reachable after {timeout}s: {last_err}")
