"""
ERNIE 4.5 Inference Server for Doclyst
Run this in Google Colab (free GPU) or local machine with GPU

Instructions:
1. Open Google Colab: https://colab.research.google.com
2. Select GPU runtime: Runtime > Change runtime type > T4 GPU
3. Copy this code and run
4. Copy the ngrok URL to your .env file as ERNIE_LOCAL_URL
"""

# ============================================
# STEP 1: Install dependencies (run first)
# ============================================
# !pip install transformers torch flask pyngrok accelerate

# ============================================
# STEP 2: Run this code
# ============================================

from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)

# Load ERNIE 4.5 model
print("Loading ERNIE 4.5 model...")
MODEL_NAME = "baidu/ERNIE-4.5-0.3B-PT"  # Lightweight version

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
print("Model loaded!")

@app.route('/generate', methods=['POST'])
def generate():
    """Generate text from prompt."""
    data = request.json
    prompt = data.get('prompt', '')
    max_tokens = data.get('max_tokens', 512)
    temperature = data.get('temperature', 0.7)
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove the prompt from response
    response = response[len(prompt):].strip()
    
    return jsonify({"text": response})

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    """
    Analyze image with ERNIE-VL.
    Note: Requires ERNIE-VL model for actual image analysis.
    This is a placeholder that returns the prompt response.
    """
    data = request.json
    prompt = data.get('prompt', '')
    # image_data = data.get('image', '')  # base64 encoded
    
    # For text-only model, just process the prompt
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = response[len(prompt):].strip()
    
    return jsonify({"text": response})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model": MODEL_NAME})

# ============================================
# STEP 3: Start server with ngrok (for Colab)
# ============================================

if __name__ == '__main__':
    # For Colab: use ngrok to expose the server
    try:
        from pyngrok import ngrok
        
        # Start ngrok tunnel
        public_url = ngrok.connect(5001)
        print(f"\n{'='*50}")
        print(f"🚀 ERNIE Server is running!")
        print(f"📍 Public URL: {public_url}")
        print(f"{'='*50}")
        print(f"\nAdd this to your .env file:")
        print(f"ERNIE_LOCAL_URL={public_url}")
        print(f"{'='*50}\n")
        
    except ImportError:
        print("Running locally on http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001)
