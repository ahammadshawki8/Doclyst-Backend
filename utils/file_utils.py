import os
import uuid
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_temp_file(file) -> str:
    """Save uploaded file temporarily and return path."""
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, unique_name)
    file.save(filepath)
    return filepath

def cleanup_file(filepath: str) -> None:
    """Delete temporary file after processing."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Warning: Could not delete temp file {filepath}: {e}")

def get_file_extension(filename: str) -> str:
    """Get lowercase file extension."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
