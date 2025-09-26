# proxy.py (Updated for Render)
from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client
import os
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Gradio client
try:
    client = Client("DINESH03032005/topic-extension")
    logger.info("Gradio client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gradio client: {e}")
    client = None

@app.route('/')
def home():
    return jsonify({
        "status": "Proxy server is running", 
        "message": "Use /predict endpoint",
        "version": "1.0"
    })

@app.route('/predict', methods=['POST'])
def predict():
    if client is None:
        return jsonify({
            "success": False,
            "error": "Gradio client not initialized"
        }), 500
        
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' in request body"}), 400
        
        text = data['text']
        
        # Validate text length
        if len(text.strip()) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400
            
        if len(text) > 10000:  # Limit text length
            return jsonify({"error": "Text too long. Maximum 10000 characters allowed"}), 400
        
        # Call the Gradio Space
        result = client.predict(text, api_name="/predict")
        
        # Convert to string if needed
        if hasattr(result, 'format') and callable(result.format):
            result = str(result)
        
        logger.info(f"Successfully processed text of length: {len(text)}")
        
        return jsonify({
            "success": True,
            "input_length": len(text),
            "result": result,
            "message": "Successfully processed"
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health')
def health():
    if client is None:
        return jsonify({"status": "unhealthy", "error": "Gradio client not available"}), 500
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)