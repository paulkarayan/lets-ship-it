FROM python:3.13

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync

COPY app/ app/

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]