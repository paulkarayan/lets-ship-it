# A baby FastAPI App

I'm going to assume you can do minimal Python.

I'm using `uv` for package management, pytest for application tests, and a fairly typical FastAPI application structure where our server is at  `app/main.py`.

You can run this with whatever you want, in fact, it's a good opportunity to test your knowledge - but then you're not going to get the sweet sweet validation that I've got going on here.

## Running the API server

I just put a health check endpoint in, so this is pretty boring - but we'll build on it.

To run our app, your first instinct might be:

```bash
python ./app/main.py
```

That won't work. `main.py` may define a FastAPI app, but there's nothing to run it.
FastAPI is a framework - it needs a server; we'll use `uvicorn` for that and test with `curl`

```bash
uvicorn app.main:app --reload --port 8042 # avoiding collisions :)

# separate process
curl http://localhost:8042/healthz
```

The output shold be something like:
```
➜  lets-ship-it git:(main) curl http://localhost:8042/healthz       ()
{"status":"ok"}%
```

## Running the tests

I also provide you with some minimal tests we can build off of; run it like so:

```bash
uv run pytest
```

Notice something? The tests pass without the server running.

`TestClient` doesn't make real HTTP requests. It calls your FastAPI app in-process using ASGI, simulating requests against the app object you imported. No network, no server. It's good for unit tests but it's not a real integration test.

To make it a real integration test, use `requests` or `httpx`. Run and then hit the actual server.

```bash
curl http://localhost:8042/healthz
```

```
➜  lets-ship-it git:(main) ✗ uv run pytest                          ()
========================= test session starts =========================
platform darwin -- Python 3.13.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/pk/side/lets-ship-it
configfile: pyproject.toml
testpaths: tests/pytest
plugins: anyio-4.12.1
collected 2 items                                                     

tests/pytest/test_healthz.py ..                                 [100%]

========================== 2 passed in 0.22s ==========================
```


The catch is that you need that port hardcoded. If you're spinning up a lot of containers, that gets annoying fast. Hold onto that thought.
