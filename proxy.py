from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hugging Face Space API URL
SPACE_API_URL = "https://dinesh03032005-topic-extension.hf.space/api/predict"

@app.route('/')
def home():
    return jsonify({
        "status": "Proxy server is running", 
        "message": "Use /predict endpoint",
        "version": "1.2",
        "mode": "Direct HTTP to HF Space"
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
        
        # Call Hugging Face Space directly via HTTP
        response = requests.post(
            SPACE_API_URL,
            json={"data": [text]},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result_data = response.json()
            if "data" in result_data:
                result = result_data["data"][0]
                
                logger.info(f"Successfully processed text of length: {len(text)}")
                
                return jsonify({
                    "success": True,
                    "input_length": len(text),
                    "result": result,
                    "message": "Successfully processed"
                })
            else:
                raise Exception(f"Unexpected response format: {result_data}")
        else:
            raise Exception(f"HF Space API error: HTTP {response.status_code}")
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health')
def health():
    try:
        # Simple health check without calling HF API
        return jsonify({"status": "healthy", "service": "ready"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
