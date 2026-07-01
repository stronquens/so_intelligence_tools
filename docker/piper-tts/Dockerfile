FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libespeak-ng1 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir fastapi "uvicorn[standard]" huggingface_hub piper-tts

COPY server.py /app/server.py

EXPOSE 9010

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9010"]
