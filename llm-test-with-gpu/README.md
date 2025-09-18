# DeepSeek Chat with GPU Monitoring

ChatGPT-like system using DeepSeek models on GPU with Grafana monitoring.

## Run

```bash
# Use app default model
make run

# Or pick a model at runtime
make run model=deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B
```

## URLs

- Chat: http://localhost:5000
- Grafana: http://localhost:3000/d/gpu-cpu-dashboard/gpu-and-cpu-monitoring

## Notes

- Default model is defined only in `app/app.py`. `MODEL_NAME` can override it at runtime via `make run model=...`.
- To explore models with size hints:
  - `make list-models`
  - `make list-models filter=coder`
  - `make list-models memory=8`
  - Example: `unsloth/DeepSeek-R1-Distill-Llama-8B-unsloth-bnb-4bit` (~6–8GB VRAM, ~6GB download)
- https://huggingface.co/models

## Examples (tested)

```bash
# Default small
make run model=deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B

# 8B 4-bit (bnb)
make run model=unsloth/DeepSeek-R1-Distill-Llama-8B-unsloth-bnb-4bit

# AWQ quantized
make run model=TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ

# GGUF (llama.cpp backend)
make run model=unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF
```
