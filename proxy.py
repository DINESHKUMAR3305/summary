from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client
import logging
import os

app = Flask(__name__)
CORS(app)

# Configure logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Gradio client with error handling
try:
    client = Client("DINESH03032005/topic-extension")
    logger.info("✅ Gradio client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Gradio client: {e}")
    client = None

@app.route('/')
def home():
    return jsonify({
        "status": "Proxy server is running", 
        "message": "Use /predict endpoint",
        "version": "1.0",
        "model": "DINESH03032005/topic-extension"
    })

@app.route('/predict', methods=['POST'])
def predict():
    if client is None:
        return jsonify({
            "success": False,
            "error": "Gradio client not initialized. Please check server logs."
        }), 500
        
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' in request body"}), 400
        
        text = data['text'].strip()
        
        # Input validation
        if len(text) == 0:
            return jsonify({"error": "Text cannot be empty"}), 400
            
        if len(text) > 10000:
            return jsonify({"error": "Text too long. Maximum 10000 characters allowed"}), 400
        
        # Call the Gradio Space
        logger.info(f"Processing text of length: {len(text)}")
        result = client.predict(text, api_name="/predict")
        
        # Ensure result is properly formatted as string
        if hasattr(result, 'format') and callable(result.format):
            result = str(result)
        
        logger.info("✅ Successfully processed request")
        
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
    if client is None:
        return jsonify({
            "status": "unhealthy", 
            "error": "Gradio client not available"
        }), 500
        
    try:
        # Test the connection with a simple prediction
        test_result = client.predict("health check", api_name="/predict")
        return jsonify({
            "status": "healthy",
            "model": "connected",
            "test_result": "ok"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy", 
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Set debug=False for production
    app.run(host='0.0.0.0', port=port, debug=False)
