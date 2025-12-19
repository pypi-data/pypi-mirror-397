FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY kytchen/ kytchen/

RUN pip install --no-cache-dir -e ".[api,mcp]"

ENV KYTCHEN_DEV_MODE=0

CMD ["uvicorn", "kytchen.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
