.PHONY: help run stop list-models

MODEL ?=

# Allow lowercase override: `make run model=...`
ifdef model
MODEL := $(model)
endif

help:
	@echo "Available commands:"
	@echo "  run [model=MODEL_NAME] - Start all services"
	@echo "  stop                  - Stop all services"
	@echo "  list-models [filter=NAME] [memory=MAX_GB] - List available DeepSeek models"
	@echo ""
	@echo "Examples:"
	@echo "  make run"
	@echo "  make run model=deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
	@echo "  make list-models"
	@echo "  make list-models filter=coder"
	@echo "  make list-models memory=8"
	@echo "  make list-models filter=7b memory=20"

list-models:
	@echo "Fetching DeepSeek models from Hugging Face..."
	@echo ""
	@curl -s "https://huggingface.co/api/models?author=deepseek-ai&sort=downloads&direction=-1&limit=20" | \
	jq -r '.[] | select(.id | test("deepseek-ai/.*")) | "\(.id) (\(.downloads // 0 | . / 1000 | floor)K downloads)"' | \
	head -15 | while read line; do \
		model_id=$$(echo "$$line" | cut -d' ' -f1); \
		downloads=$$(echo "$$line" | cut -d' ' -f2-3); \
		if echo "$$model_id" | grep -q "1\.5B\|1\.3B\|1B"; then \
			size="~3GB VRAM"; \
			size_order="1"; \
			size_gb=3; \
		elif echo "$$model_id" | grep -q "6\.7B\|7B"; then \
			size="~13GB VRAM"; \
			size_order="2"; \
			size_gb=13; \
		elif echo "$$model_id" | grep -q "14B"; then \
			size="~28GB VRAM"; \
			size_order="3"; \
			size_gb=28; \
		elif echo "$$model_id" | grep -q "32B"; then \
			size="~64GB VRAM"; \
			size_order="4"; \
			size_gb=64; \
		elif echo "$$model_id" | grep -q "67B\|70B"; then \
			size="~134GB VRAM"; \
			size_order="5"; \
			size_gb=134; \
		else \
			size="~6GB VRAM"; \
			size_order="1.5"; \
			size_gb=6; \
		fi; \
		\
		# Apply name filter if specified \
		if [ -n "$(filter)" ]; then \
			if ! echo "$$model_id" | grep -qi "$(filter)"; then \
				continue; \
			fi; \
		fi; \
		\
		# Apply memory filter if specified \
		if [ -n "$(memory)" ]; then \
			if [ "$$size_gb" -gt "$(memory)" ]; then \
				continue; \
			fi; \
		fi; \
		\
		echo "$$size_order|$$model_id $$downloads ($$size)"; \
	done | sort -n | cut -d'|' -f2 || echo "Failed to fetch models from Hugging Face API"
	@echo ""
	@echo "Set a model with: make run model=MODEL_NAME (omit to use app default)"

stop:
	@docker compose down

run: stop
	@MODEL_NAME=$(MODEL) docker compose up --build -d
