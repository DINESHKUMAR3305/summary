from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import time

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy import - only load gradio_client when needed
def get_client():
    from gradio_client import Client
    return Client("DINESH03032005/topic-extension")

@app.route('/')
def home():
    return jsonify({
        "status": "Proxy server is running", 
        "message": "Use /predict endpoint",
        "version": "2.2"
    })

@app.route('/predict', methods=['POST'])
def predict():        
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' in request body"}), 400
        
        text = data['text'].strip()
        
        if len(text) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400
            
        if len(text) > 10000:
            return jsonify({"error": "Text too long. Maximum 10000 characters allowed"}), 400
        
        # Initialize client on first prediction (lazy loading)
        client = get_client()
        
        # Call the Gradio Space
        result = client.predict(text, api_name="/predict")
        
        if hasattr(result, 'format') and callable(result.format):
            result = str(result)
        
        logger.info(f"✅ Processed text length: {len(text)}")
        
        return jsonify({
            "success": True,
            "input_length": len(text),
            "result": result,
            "message": "Successfully processed"
        })
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health')
def health():
    """Ultra-simple health check that always passes"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
