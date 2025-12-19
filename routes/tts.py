"""
Text-to-Speech route using gTTS (Google Text-to-Speech)
"""
from flask import Blueprint, request, Response, jsonify
from gtts import gTTS
import io

tts_bp = Blueprint('tts', __name__)

# Language code mapping
LANG_MAP = {
    'en': 'en',
    'bn': 'bn',
    'zh': 'zh-CN',
    'hi': 'hi',
    'es': 'es'
}

@tts_bp.route('/tts', methods=['POST'])
def text_to_speech():
    """Convert text to speech audio"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        lang = data.get('language', 'en')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Map language code
        tts_lang = LANG_MAP.get(lang, 'en')
        
        # Generate speech
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        
        # Save to bytes buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return Response(
            audio_buffer.read(),
            mimetype='audio/mpeg',
            headers={
                'Content-Type': 'audio/mpeg',
                'Cache-Control': 'no-cache'
            }
        )
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({'error': str(e)}), 500
