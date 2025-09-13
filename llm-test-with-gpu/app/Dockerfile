# syntax=docker/dockerfile:1.7-labs
FROM python:3.9-slim

RUN apt-get update && apt-get install -y git build-essential cmake && rm -rf /var/lib/apt/lists/*

# Build llama-cpp-python with defaults (CPU). GPU build is optional and not required.
# To enable CUDA in the future, set: ENV CMAKE_ARGS="-DGGML_CUDA=on"

WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip3 install -r requirements.txt

COPY app.py .
COPY index.html .
EXPOSE 5000

CMD ["python3", "app.py"]
