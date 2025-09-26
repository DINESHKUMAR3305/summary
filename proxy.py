from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client
import logging
import os
import time

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for client and readiness
client = None
client_initialized = False
client_initializing = False

def initialize_gradio_client():
    """Initialize Gradio client in background"""
    global client, client_initialized, client_initializing
    
    if client_initializing or client_initialized:
        return
    
    client_initializing = True
    logger.info("🔄 Initializing Gradio client...")
    
    try:
        # This can take time - Hugging Face connection
        client = Client("DINESH03032005/topic-extension")
        client_initialized = True
        logger.info("✅ Gradio client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gradio client: {e}")
        client = None
    finally:
        client_initializing = False

# Start initialization when app starts
@app.before_first_request
def before_first_request():
    """Start client initialization when first request comes in"""
    import threading
    thread = threading.Thread(target=initialize_gradio_client)
    thread.daemon = True
    thread.start()

@app.route('/')
def home():
    return jsonify({
        "status": "Proxy server is running on Railway", 
        "message": "Use /predict endpoint",
        "version": "2.1",
        "platform": "Railway",
        "client_ready": client_initialized
    })

@app.route('/predict', methods=['POST'])
def predict():
    if not client_initialized:
        return jsonify({
            "success": False,
            "error": "Gradio client is still initializing. Please try again in 10-20 seconds.",
            "status": "initializing"
        }), 503  # Service Unavailable
        
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
    """Simple health check that doesn't depend on Gradio client"""
    try:
        # Basic health check - just see if Flask is running
        health_status = {
            "status": "healthy",
            "platform": "Railway",
            "flask": "running",
            "client_initialized": client_initialized,
            "timestamp": time.time()
        }
        
        # Only check Gradio client if it's supposed to be initialized
        if client_initialized and client is not None:
            try:
                # Quick test without full prediction
                health_status["gradio"] = "connected"
            except:
                health_status["gradio"] = "disconnected"
        else:
            health_status["gradio"] = "initializing"
            
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/ready')
def ready():
    """Readiness probe - checks if client is fully initialized"""
    if client_initialized and client is not None:
        return jsonify({
            "ready": True,
            "status": "fully_initialized",
            "timestamp": time.time()
        })
    else:
        return jsonify({
            "ready": False,
            "status": "initializing",
            "client_initialized": client_initialized,
            "timestamp": time.time()
        }), 503  # Service Unavailable

if __name__ == '__main__':
    # Start client initialization when app starts
    import threading
    thread = threading.Thread(target=initialize_gradio_client)
    thread.daemon = True
    thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
