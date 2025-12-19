from flask import Blueprint, request, jsonify
from config import Config
from utils import allowed_file, save_temp_file, cleanup_file, get_file_extension
from services.ocr_service import process_file
from services.ernie_service import analyze_medical_report, compare_medical_reports

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
        
        # Return structured response with anti-panic content
        return jsonify({
            'overallStatus': result.get('overallStatus', 'ATTENTION'),
            'summary': result.get('summary', 'Your medical report has been reviewed.'),
            'tests': result.get('findings', []),
            'disclaimer': Config.DISCLAIMER,
            'doesNotMean': result.get('doesNotMean', [
                "This does NOT mean you have a confirmed disease",
                "Abnormal values don't always indicate serious problems"
            ]),
            'nextSteps': result.get('nextSteps', [
                "Schedule a follow-up with your doctor",
                "Keep this report for your records"
            ]),
            'doctorQuestions': result.get('doctorQuestions', [
                "What do these results mean for my health?",
                "Should I do any follow-up tests?"
            ])
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

@analyze_bp.route('/compare', methods=['POST'])
def compare_reports():
    """
    Compare two medical reports (old vs new).
    
    Accepts: multipart/form-data with 'old_file' and 'new_file' fields
    Returns: JSON with comparison results
    """
    old_files = request.files.getlist('old_file')
    new_files = request.files.getlist('new_file')
    
    if not old_files or not new_files:
        return jsonify({
            'error': 'Missing files',
            'message': 'Please upload both old and new reports.'
        }), 400
    
    old_files = [f for f in old_files if f.filename != '']
    new_files = [f for f in new_files if f.filename != '']
    
    if not old_files or not new_files:
        return jsonify({
            'error': 'Missing files',
            'message': 'Please upload both old and new reports.'
        }), 400
    
    # Validate file types
    for file in old_files + new_files:
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'File "{file.filename}" is not supported.'
            }), 400
    
    filepaths = []
    
    try:
        # Process old report files
        old_texts = []
        for file in old_files:
            filepath = save_temp_file(file)
            filepaths.append(filepath)
            file_ext = get_file_extension(file.filename)
            text = process_file(filepath, file_ext)
            if text and len(text.strip()) > 10:
                old_texts.append(text)
        
        # Process new report files
        new_texts = []
        for file in new_files:
            filepath = save_temp_file(file)
            filepaths.append(filepath)
            file_ext = get_file_extension(file.filename)
            text = process_file(filepath, file_ext)
            if text and len(text.strip()) > 10:
                new_texts.append(text)
        
        old_combined = "\n\n".join(old_texts)
        new_combined = "\n\n".join(new_texts)
        
        if not old_combined or not new_combined:
            return jsonify({
                'error': 'No text found',
                'message': "Couldn't read text from one or both reports."
            }), 400
        
        # Compare reports
        result = compare_medical_reports(old_combined, new_combined)
        
        return jsonify({
            'overallStatus': result.get('overallStatus', 'ATTENTION'),
            'summary': result.get('summary', 'Reports compared.'),
            'tests': result.get('findings', []),
            'disclaimer': Config.DISCLAIMER,
            'isComparison': True,
            'comparison': result.get('comparison', {}),
            'doesNotMean': result.get('doesNotMean', []),
            'nextSteps': result.get('nextSteps', []),
            'doctorQuestions': result.get('doctorQuestions', [])
        }), 200
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({
            'error': 'Comparison failed',
            'message': "Couldn't compare the reports. Please try again."
        }), 500
    
    finally:
        for filepath in filepaths:
            cleanup_file(filepath)


@analyze_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'doclyst-backend'}), 200
