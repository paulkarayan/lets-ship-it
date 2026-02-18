# create the structure
uv, app/main.py, the pytest setup etc

# run the app
python ./app/main.py 
^^ won't work because we just defined a FastApi App but didnt run it.

uvicorn app.main:app --reload

# run the tests
uv run pytest

see anything wrong?

note taht the tests work without the server running.

TestClient doesn't make real HTTP requests. It calls your FastAPI
app directly in-process using ASGI — no network, no port, no server
needed. It just simulates requests against the app object you
imported.

# make it a real integration test

use `requests` or `httpx`

this is equivalent of:
curl http://localhost:8042/healthz


