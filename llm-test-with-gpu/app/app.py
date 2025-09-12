from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import threading
import time

app = Flask(__name__)
CORS(app)

# Global variables for model status
model_loading = True
model_ready = False
model_error = None
model = None
tokenizer = None

def load_model():
    global model_loading, model_ready, model_error, model, tokenizer
    try:
        print("Loading model...")
        model_name = "deepseek-ai/deepseek-coder-1.3b-instruct"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        print("Model loaded successfully!")
        model_loading = False
        model_ready = True
    except Exception as e:
        print(f"Error loading model: {e}")
        model_error = str(e)
        model_loading = False
        model_ready = False

# Start model loading in background
threading.Thread(target=load_model, daemon=True).start()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/status')
def status():
    return jsonify({
        'loading': model_loading,
        'ready': model_ready,
        'error': model_error
    })

@app.route('/chat', methods=['POST'])
def chat():
    global model, tokenizer

    # Check if model is ready
    if model_loading:
        return jsonify({'error': 'Model is still loading, please wait...'}), 202

    if not model_ready or model is None or tokenizer is None:
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

        # Tokenize and generate
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = inputs.cuda()

        print("Generating response...")
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=64,  # Reduced for faster response
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
