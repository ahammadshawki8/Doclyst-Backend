from flask import Blueprint, request, jsonify
from config import Config
from utils import allowed_file, save_temp_file, cleanup_file, get_file_extension
from services.ocr_service import process_file
from services.ernie_service import analyze_medical_report

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route('/analyze', methods=['POST'])
def analyze_report():
    """
    Universal endpoint for analyzing medical reports.
    
    Accepts: multipart/form-data with 'file' field (single or multiple files)
    Supported: PDF, JPG, PNG, JPEG
    
    Returns: JSON with status, summary, tests/findings, disclaimer
    """
    # Get all files (supports both single 'file' and multiple 'files')
    files = request.files.getlist('file')
    
    # Also check for 'files' field name
    if not files:
        files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify({
            'error': 'No file provided',
            'message': 'Please upload a medical report file.'
        }), 400
    
    # Filter out empty files
    files = [f for f in files if f.filename != '']
    
    if not files:
        return jsonify({
            'error': 'No file selected',
            'message': 'Please select a file to upload.'
        }), 400
    
    # Validate all file types
    for file in files:
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'File "{file.filename}" is not supported. Please upload PDF, JPG, PNG, or JPEG files.'
            }), 400
    
    filepaths = []
    all_extracted_text = []
    
    try:
        # Process each file
        for file in files:
            filepath = save_temp_file(file)
            filepaths.append(filepath)
            file_ext = get_file_extension(file.filename)
            
            print(f"[OCR] Processing file {len(filepaths)}/{len(files)}: {file.filename}")
            
            # Extract text from this file
            extracted_text = process_file(filepath, file_ext)
            
            if extracted_text and len(extracted_text.strip()) > 10:
                all_extracted_text.append(extracted_text)
                print(f"[OCR] Extracted {len(extracted_text)} chars from {file.filename}")
            else:
                print(f"[OCR] No text found in {file.filename}")
        
        # Combine all extracted text
        combined_text = "\n\n--- Page Break ---\n\n".join(all_extracted_text)
        
        print(f"[OCR] Total extracted: {len(combined_text)} chars from {len(files)} file(s)")
        
        if not combined_text or len(combined_text.strip()) < 10:
            return jsonify({
                'error': 'No text found',
                'message': "We couldn't read any text from the uploaded files. Please try clearer images."
            }), 400
        
        # Analyze combined text
        result = analyze_medical_report(combined_text)
        
        # Return structured response
        return jsonify({
            'overallStatus': result.get('overallStatus', 'ATTENTION'),
            'summary': result.get('summary', 'Your medical report has been reviewed.'),
            'tests': result.get('findings', []),
            'disclaimer': Config.DISCLAIMER
        }), 200
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({
            'error': 'Processing failed',
            'message': "We couldn't process your files. Please try clearer images."
        }), 500
    
    finally:
        # Cleanup all temp files
        for filepath in filepaths:
            cleanup_file(filepath)

@analyze_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'doclyst-backend'}), 200
