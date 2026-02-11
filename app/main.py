from fastapi import FastAPI

app = FastAPI(title="k8s-is-g8s")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
