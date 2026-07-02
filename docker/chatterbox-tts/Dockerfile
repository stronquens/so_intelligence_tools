FROM pytorch/pytorch:2.7.1-cuda12.6-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/var/lib/chatterbox-tts/hf
ENV TRANSFORMERS_CACHE=/var/lib/chatterbox-tts/hf
ENV PIP_CACHE_DIR=/var/lib/chatterbox-tts/pip

RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir fastapi "uvicorn[standard]" huggingface_hub safetensors \
    && python -m pip install --no-cache-dir git+https://github.com/resemble-ai/chatterbox.git \
    && python -m pip uninstall -y -q torchvision || true

COPY server.py /app/server.py
COPY voices/ /app/voices/

EXPOSE 9011

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9011"]
