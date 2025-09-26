from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client
import os
import logging
import requests

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GradioHTTPClient:
    def __init__(self, space_name):
        self.base_url = f"https://{space_name.replace('_', '-')}.hf.space"
        self.api_url = f"{self.base_url}/api/predict"
        logger.info(f"Initialized HTTP client for: {self.base_url}")
    
    def predict(self, text, api_name="/predict"):
        try:
            response = requests.post(
                self.api_url,
                json={"data": [text]},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result:
                    return result["data"][0]  # Extract the prediction result
                else:
                    raise Exception(f"Unexpected response format: {result}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise e

# Initialize the HTTP client (WebSocket-free)
try:
    client = GradioHTTPClient("DINESH03032005/topic-extension")
    logger.info("HTTP client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize HTTP client: {e}")
    client = None

@app.route('/')
def home():
    return jsonify({
        "status": "Proxy server is running", 
        "message": "Use /predict endpoint",
        "version": "1.1",
        "mode": "HTTP-only (WebSocket-free)"
    })

@app.route('/predict', methods=['POST'])
def predict():
    if client is None:
        return jsonify({
            "success": False,
            "error": "HTTP client not initialized"
        }), 500
        
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' in request body"}), 400
        
        text = data['text']
        
        # Validate text length
        if len(text.strip()) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400
            
        if len(text) > 10000:
            return jsonify({"error": "Text too long. Maximum 10000 characters allowed"}), 400
        
        # Call the Gradio Space using HTTP
        result = client.predict(text)
        
        logger.info(f"Successfully processed text of length: {len(text)}")
        
        return jsonify({
            "success": True,
            "input_length": len(text),
            "result": result,
            "message": "Successfully processed via HTTP"
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
        return jsonify({"status": "unhealthy", "error": "HTTP client not available"}), 500
    
    # Test the connection
    try:
        test_result = client.predict("test")
        return jsonify({"status": "healthy", "test_result": "connection_ok"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
