# create the structure
uv, app/main.py, the pytest setup etc

# run the app
python ./app/main.py
^^ won't work because we just defined a FastApi App but didnt run it.

uvicorn app.main:app --reload

# run the tests
uv run pytest

see anything wrong?

note that the tests work without the server running.

TestClient doesn't make real HTTP requests. It calls your FastAPI
app directly in-process using ASGI — no network, no port, no server
needed. It just simulates requests against the app object you
imported.

# make it a real integration test

use `requests` or `httpx`

this is equivalent of:
curl http://localhost:8042/healthz

note that this requires you to have that port specified. that's kind of a pain
if you're spinning up a lot of containers. hold onto that thought.


➜  lets-ship-it git:(main) ✗ uv run pytest                         ()
======================== test session starts =========================
platform darwin -- Python 3.13.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/pk/side/lets-ship-it
configfile: pyproject.toml
testpaths: tests/pytest
plugins: anyio-4.12.1
collected 2 items

tests/pytest/test_healthz.py ..                                [100%]

========================= 2 passed in 0.18s ==========================


