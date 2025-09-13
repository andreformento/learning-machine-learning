from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
from typing import Optional
from huggingface_hub import list_repo_files, hf_hub_download
from llama_cpp import Llama
import threading
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Model configuration from environment (single source of default)
_DEFAULT_MODEL = 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B'
_ENV_MODEL = os.getenv('MODEL_NAME')
MODEL_NAME = _ENV_MODEL.strip() if (_ENV_MODEL is not None and _ENV_MODEL.strip()) else _DEFAULT_MODEL

# Global variables for model status
model_loading = True
model_ready = False
model_error = None
model = None
tokenizer = None
is_llama_cpp = False
loading_progress = 0
loading_stage = "Initializing..."
loading_details = ""

def load_model():
    global model_loading, model_ready, model_error, model, tokenizer, loading_progress, loading_stage, loading_details, is_llama_cpp
    try:
        print(f"Loading model: {MODEL_NAME}")

        model_name_lower = MODEL_NAME.lower()
        if "gguf" in model_name_lower:
            # Stage 1: Find and download GGUF
            loading_stage = "Resolving GGUF file..."
            loading_progress = 10
            loading_details = "Listing repo files..."
            files = list_repo_files(MODEL_NAME)
            ggufs = [f for f in files if f.endswith('.gguf')]
            if not ggufs:
                raise RuntimeError("No .gguf files found in repo")
            # Prefer Q4_K_M, else first
            preferred: Optional[str] = next((f for f in ggufs if 'Q4_K_M' in f or 'Q4_K_S' in f), ggufs[0])

            loading_stage = "Downloading GGUF..."
            loading_progress = 30
            loading_details = preferred
            model_path = hf_hub_download(repo_id=MODEL_NAME, filename=preferred)

            # Stage 2: Load llama.cpp
            loading_stage = "Loading llama.cpp model..."
            loading_progress = 60
            loading_details = preferred
            # Try offloading some layers to GPU if available
            n_gpu_layers = 20 if torch.cuda.is_available() else 0
            model = Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=n_gpu_layers)
            tokenizer = None
            is_llama_cpp = True
        else:
            # Stage 1: Loading tokenizer
            loading_stage = "Loading tokenizer..."
            loading_progress = 10
            loading_details = "Downloading tokenizer files..."
            print("Loading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True, trust_remote_code=True)

            # Stage 2: Loading model
            loading_stage = "Loading model..."
            loading_progress = 30
            loading_details = "Downloading model files..."
            print("Loading model...")
            quantization_config = None
            if "bnb-4bit" in model_name_lower or "int4" in model_name_lower:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=torch.float16
                )
            elif "awq" in model_name_lower:
                quantization_config = None
            elif "gptq" in model_name_lower:
                quantization_config = None

            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                quantization_config=quantization_config
            )

        # Stage 3: Model ready
        loading_stage = "Model ready!"
        loading_progress = 100
        loading_details = "Model loaded successfully"
        print("Model loaded successfully!")
        model_loading = False
        model_ready = True

    except Exception as e:
        print(f"Error loading model: {e}")
        model_error = str(e)
        loading_stage = "Error loading model"
        loading_progress = 0
        loading_details = str(e)
        model_loading = False
        model_ready = False

# Start model loading in background
threading.Thread(target=load_model, daemon=True).start()

@app.route('/')
def index():
    return send_file('index.html')

def process_message(message):
    """Process a message and return the response"""
    global model, tokenizer

    if model_loading:
        return "Model is still loading, please wait..."

    # Consider ready if model is loaded
    if not model_ready or model is None:
        return f"Model not ready: {model_error}"

    try:
        print(f"Processing message: {message[:50]}...")

        # Format prompt
        prompt = f"Human: {message}\n\nAssistant:"

        if is_llama_cpp:
            print("Generating with llama.cpp...")
            out = model(prompt=prompt, max_tokens=256, temperature=0.7)
            response = out["choices"][0]["text"]
            print(f"Generated response: {response[:50]}...")
            return response.strip()
        else:
            # Tokenize and generate with transformers
            inputs = tokenizer.encode(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = inputs.cuda()

            print("Generating response...")
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_new_tokens=256,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    attention_mask=torch.ones_like(inputs),
                    repetition_penalty=1.1
                )

            response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            print(f"Generated response: {response[:50]}...")
            return response.strip()

    except torch.cuda.OutOfMemoryError:
        return "GPU out of memory. Try a shorter message or restart the service."
    except Exception as e:
        print(f"Error in process_message: {e}")
        return f"Generation error: {str(e)}"


@app.route('/status')
def status():
    return jsonify({
        'loading': model_loading,
        'ready': model_ready,
        'error': model_error,
        'model_name': MODEL_NAME,
        'loading_progress': loading_progress,
        'loading_stage': loading_stage,
        'loading_details': loading_details
    })

@app.route('/chat', methods=['POST'])
def chat():
    global model, tokenizer

    # Check if model is ready
    if model_loading:
        return jsonify({'error': 'Model is still loading, please wait...'}), 202

    # Consider ready if model is loaded
    if not model_ready or model is None:
        return jsonify({'error': f'Model not ready: {model_error}'}), 503

    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    message = data['message']
    if not message.strip():
        return jsonify({'error': 'Empty message'}), 400

    try:
        print(f"Processing message: {message[:50]}...")

        # Format prompt
        prompt = f"Human: {message}\n\nAssistant:"

        if is_llama_cpp:
            print("Generating with llama.cpp...")
            out = model(prompt=prompt, max_tokens=256, temperature=0.7)
            response = out["choices"][0]["text"].strip()
            print(f"Generated response: {response[:50]}...")
            return jsonify({'response': response})
        else:
            # Tokenize and generate
            inputs = tokenizer.encode(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = inputs.cuda()

            print("Generating response...")
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_new_tokens=256,  # Increased for better responses
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    attention_mask=torch.ones_like(inputs),
                    repetition_penalty=1.1
                )

            response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            print(f"Generated response: {response[:50]}...")
            return jsonify({'response': response.strip()})

    except torch.cuda.OutOfMemoryError:
        return jsonify({'error': 'GPU out of memory. Try a shorter message or restart the service.'}), 507
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': f'Generation error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
