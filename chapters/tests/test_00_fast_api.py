"""Verify code blocks from chapter 00 — A baby FastAPI App."""

import json
import subprocess

from .helpers import background, find_repo_root, run, wait_for_http

ROOT = str(find_repo_root())

PORT = 18042  # offset to avoid collisions with a running dev server


class TestChapter00:
    def test_python_main_doesnt_run(self):
        """python ./app/main.py should exit without serving anything."""
        result = subprocess.run(
            ["python", "./app/main.py"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=5,
        )
        # It exits 0 but produces no server — just loads and quits.
        # The chapter says "doesn't work" meaning it won't serve requests.
        assert result.returncode == 0

    def test_uvicorn_serves_healthz(self):
        """Start uvicorn, hit /healthz, expect {"status":"ok"}."""
        cmd = f"uv run uvicorn app.main:app --port {PORT}"
        with background(cmd, "Uvicorn running", cwd=ROOT):
            body = wait_for_http(f"http://localhost:{PORT}/healthz")
            data = json.loads(body)
            assert data == {"status": "ok"}

    def test_pytest_passes(self):
        """uv run pytest exits 0 and collects tests."""
        out = run("uv run pytest", cwd=ROOT)
        # run() raises on non-zero exit, so reaching here means pytest passed.
        # Verify it actually ran something (not "no tests ran").
        assert "no tests ran" not in out
