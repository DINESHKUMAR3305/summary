from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client
import logging
import os

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Gradio client
try:
    client = Client("DINESH03032005/topic-extension")
    logger.info("✅ Gradio client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Gradio client: {e}")
    client = None

@app.route('/')
def home():
    return jsonify({
        "status": "Proxy server is running on Railway", 
        "message": "Use /predict endpoint",
        "version": "2.0",
        "platform": "Railway"
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
        
        text = data['text'].strip()
        
        if len(text) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400
            
        if len(text) > 10000:
            return jsonify({"error": "Text too long. Maximum 10000 characters allowed"}), 400
        
        # Call the Gradio Space
        result = client.predict(text, api_name="/predict")
        
        if hasattr(result, 'format') and callable(result.format):
            result = str(result)
        
        logger.info(f"✅ Processed text length: {len(text)}")
        
        return jsonify({
            "success": True,
            "input_length": len(text),
            "result": result,
            "message": "Successfully processed on Railway"
        })
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health')
def health():
    if client is None:
        return jsonify({"status": "unhealthy", "error": "Client not available"}), 500
    
    try:
        test_result = client.predict("health check", api_name="/predict")
        return jsonify({"status": "healthy", "platform": "Railway"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    # CRITICAL FIX: Use Railway's PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    # Use production server instead of development server
    app.run(host='0.0.0.0', port=port, debug=False)
