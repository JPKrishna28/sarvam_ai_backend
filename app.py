from flask import Flask, request, jsonify
from flask_cors import CORS
from sarvamai import SarvamAI
import os
import requests
from datetime import datetime, timezone
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Language code mapping
SUPPORTED_LANGUAGES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Bengali": "bn-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN"
}

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Return the list of supported languages"""
    return jsonify({
        "success": True,
        "languages": list(SUPPORTED_LANGUAGES.keys())
    })

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate text from source language to target language"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        }), 400
    
    text = data.get('text')
    source_lang = data.get('sourceLang')
    target_lang = data.get('targetLang')
    
    # Validate input
    if not text or not source_lang or not target_lang:
        return jsonify({
            "success": False,
            "message": "Missing required fields: text, sourceLang, targetLang"
        }), 400
    
    if source_lang == target_lang:
        return jsonify({
            "success": False,
            "message": "Source and target languages are the same"
        }), 400
    
    # Get API key from environment variable or use the provided one
    api_key = os.environ.get('SARVAM_API_KEY', "sk_03m67v1q_5xiVf8LZ8G6L3c1vbbJw6TDk")
    
    try:
        client = SarvamAI(api_subscription_key=api_key)
        
        response = client.text.translate(
            input=text,
            source_language_code=SUPPORTED_LANGUAGES[source_lang],
            target_language_code=SUPPORTED_LANGUAGES[target_lang],
            speaker_gender="Male",
            mode="classic-colloquial",
            model="mayura:v1",
            enable_preprocessing=False,
        )
        
        # Get current UTC time
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        return jsonify({
            "success": True,
            "translated_text": response.translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "timestamp": current_time,
            "user": "JPKrishna28"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech using Sarvam API"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "message": "No data provided"
        }), 400
    
    text = data.get('text')
    language_code = data.get('languageCode')
    
    if not text or not language_code:
        return jsonify({
            "success": False,
            "message": "Missing required fields: text, languageCode"
        }), 400
    
    # Get API key from environment variable or use the provided one
    api_key = os.environ.get('SARVAM_API_KEY', "sk_03m67v1q_5xiVf8LZ8G6L3c1vbbJw6TDk")
    
    try:
        # Call Sarvam AI's text-to-speech API
        response = requests.post(
            "https://api.sarvam.ai/text-to-speech",
            headers={
                "api-subscription-key": api_key
            },
            json={
                "text": text,
                "target_language_code": language_code
            },
        )
        
        if response.status_code == 200:
            result = response.json()
            # If the API returns audio as base64, we can pass it directly
            # If it returns a URL, we might need to fetch the audio
            return jsonify({
                "success": True,
                "audio_data": result.get("audio_content"),
                "message": "Text-to-speech conversion successful"
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Error from TTS API: {response.text}"
            }), response.status_code
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/api/system-info', methods=['GET'])
def get_system_info():
    """Return current system information"""
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({
        "success": True,
        "timestamp": current_time,
        "user": "JPKrishna28"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)