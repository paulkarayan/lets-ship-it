# A FastAPI App

Set up the project structure: `uv` for package management, `app/main.py` for the API, pytest for tests.

## Running it

Your first instinct might be:

```bash
python ./app/main.py
```

That won't work. You defined a FastAPI app, but nothing runs it. FastAPI is a framework — it needs a server.

```bash
uvicorn app.main:app --reload
```

## Running the tests

```bash
uv run pytest
```

Notice something? The tests pass without the server running.

`TestClient` doesn't make real HTTP requests. It calls your FastAPI app in-process using ASGI. No network, no port, no server. It simulates requests against the app object you imported.

Good for unit tests. Not a real integration test.

## Make it a real integration test

Use `requests` or `httpx`. Hit the actual server.

```bash
curl http://localhost:8042/healthz
```

This is the same thing, but from Python instead of the terminal.

The catch: you need that port hardcoded. If you're spinning up a lot of containers, that gets annoying fast. Hold onto that thought.

## Both passing

```
➜ uv run pytest
======================== test session starts =========================
platform darwin -- Python 3.13.3, pytest-9.0.2, pluggy-1.6.0
collected 2 items

tests/pytest/test_healthz.py ..                                [100%]

========================= 2 passed in 0.18s ==========================
```
