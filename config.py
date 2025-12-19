import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'doclyst-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # File Upload
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'temp_uploads')
    
    # LLM API Keys
    
    # PRIMARY: Groq (free, fast)
    # Get key: https://console.groq.com/keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # FALLBACK: ERNIE (sponsor)
    # Get token: https://aistudio.baidu.com/index/accessToken
    ERNIE_ACCESS_TOKEN = os.getenv('ERNIE_ACCESS_TOKEN', '')
    
    # Safety
    DISCLAIMER = "Doclyst does not provide medical advice. This explanation is for understanding only."
