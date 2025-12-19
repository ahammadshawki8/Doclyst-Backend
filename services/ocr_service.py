import os
import time
import base64
import requests
from utils.text_cleaner import clean_ocr_text

# OCR.space free API key
OCR_SPACE_KEY = "K85553768788957"

def extract_with_ocr_space(image_path: str) -> str:
    """PRIMARY: OCR using OCR.space (fast, reliable)."""
    try:
        print("[OCR] Using OCR.space (primary)...")
        
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        ext = os.path.splitext(image_path)[1].lower().replace('.', '')
        if ext == 'jpg':
            ext = 'jpeg'
        
        payload = {
            'apikey': OCR_SPACE_KEY,
            'base64Image': f'data:image/{ext};base64,{image_data}',
            'language': 'eng',
            'isOverlayRequired': False,
            'OCREngine': 2
        }
        
        response = requests.post("https://api.ocr.space/parse/image", data=payload, timeout=30)
        
        if response.ok:
            result = response.json()
            if result.get('ParsedResults'):
                text = result['ParsedResults'][0].get('ParsedText', '')
                if text:
                    print(f"[OCR] OCR.space success: {len(text)} chars")
                    return text
        
        print(f"[OCR] OCR.space failed: {response.status_code}")
        return ""
        
    except Exception as e:
        print(f"[OCR] OCR.space error: {e}")
        return ""

def extract_with_paddleocr(image_path: str) -> str:
    """FALLBACK: OCR using PaddleOCR Gradio (sponsor)."""
    try:
        from gradio_client import Client, handle_file
        
        print("[OCR] Using PaddleOCR (sponsor fallback)...")
        client = Client("https://app-u613z0mda075e806.aistudio-app.com/")
        
        result = client.predict(
            fp=handle_file(image_path),
            use_chart=False,
            use_unwarping=False,
            use_orientation=False,
            api_name="/parse_doc_router"
        )
        
        if result and len(result) >= 3:
            text = clean_ocr_text(result[2])
            print(f"[OCR] PaddleOCR success: {len(text)} chars")
            return text
        return ""
        
    except Exception as e:
        print(f"[OCR] PaddleOCR error: {e}")
        return ""

def extract_text_from_image(image_path: str) -> str:
    """Extract text from image."""
    print(f"[OCR] Processing: {os.path.basename(image_path)}")
    start = time.time()
    
    # Primary: OCR.space
    text = extract_with_ocr_space(image_path)
    if text and len(text.strip()) > 30:
        print(f"[OCR] Done in {time.time()-start:.1f}s")
        return clean_ocr_text(text)
    
    # Fallback: PaddleOCR (sponsor)
    text = extract_with_paddleocr(image_path)
    if text and len(text.strip()) > 30:
        print(f"[OCR] Done in {time.time()-start:.1f}s")
        return text
    
    print("[OCR] All OCR methods failed")
    return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF."""
    print(f"[OCR] Processing PDF: {os.path.basename(pdf_path)}")
    
    # Primary: OCR.space (supports PDF)
    try:
        with open(pdf_path, 'rb') as f:
            response = requests.post(
                "https://api.ocr.space/parse/image",
                files={'file': f},
                data={'apikey': OCR_SPACE_KEY, 'language': 'eng', 'OCREngine': 2},
                timeout=60
            )
            if response.ok:
                result = response.json()
                if result.get('ParsedResults'):
                    text = result['ParsedResults'][0].get('ParsedText', '')
                    if text and len(text) > 30:
                        print(f"[OCR] OCR.space PDF success: {len(text)} chars")
                        return clean_ocr_text(text)
    except Exception as e:
        print(f"[OCR] OCR.space PDF error: {e}")
    
    # Fallback: PaddleOCR (sponsor)
    return extract_with_paddleocr(pdf_path)

def process_file(filepath: str, file_extension: str) -> str:
    """Process file and return extracted text."""
    if file_extension == 'pdf':
        return extract_text_from_pdf(filepath)
    elif file_extension in ['png', 'jpg', 'jpeg']:
        return extract_text_from_image(filepath)
    else:
        raise ValueError(f"Unsupported: {file_extension}")
