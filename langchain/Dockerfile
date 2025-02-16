# Use an Ubuntu base image
FROM ubuntu:24.04
# Set environment variables to prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
# Install dependencies
RUN apt update && apt install -y curl
# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh
# Download and preload the Deepseek-r1 8B model
RUN ollama serve & (sleep 3 && ollama pull deepseek-r1:8b)
# Expose the port for API access (optional)
EXPOSE 11434
# Run Ollama as the default process
CMD ["ollama", "serve"]
