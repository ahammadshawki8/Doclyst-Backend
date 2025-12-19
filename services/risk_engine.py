from typing import List, Dict, Any

def calculate_urgency(parsed_tests: List[Dict[str, Any]]) -> str:
    """
    Calculate overall urgency level based on test results.
    Rule-based logic - NO AI involved.
    
    Returns: 'NORMAL', 'ATTENTION', or 'URGENT'
    """
    if not parsed_tests:
        return 'ATTENTION'  # Default when no tests parsed
    
    urgent_count = 0
    attention_count = 0
    
    for test in parsed_tests:
        value = test['value']
        min_val = test['min']
        max_val = test['max']
        
        # Critical thresholds (significantly out of range)
        if value < min_val * 0.7 or value > max_val * 1.4:
            urgent_count += 1
        # Moderate deviation
        elif value < min_val * 0.8 or value > max_val * 1.2:
            attention_count += 1
        # Mild deviation
        elif value < min_val or value > max_val:
            attention_count += 0.5
    
    # Determine overall status
    if urgent_count >= 1:
        return 'URGENT'
    elif attention_count >= 2:
        return 'ATTENTION'
    elif attention_count > 0:
        return 'ATTENTION'
    else:
        return 'NORMAL'

def get_urgency_for_image() -> str:
    """
    Default urgency for image-based reports (ECG/X-ray).
    Always returns ATTENTION since we can't diagnose from images.
    """
    return 'ATTENTION'

def get_status_message(status: str) -> str:
    """Get a friendly message for each status level."""
    messages = {
        'NORMAL': "Everything looks good! Your results are within normal ranges.",
        'ATTENTION': "Some values need attention. Consider discussing with your doctor.",
        'URGENT': "Some results may need prompt attention. Please consult a doctor soon."
    }
    return messages.get(status, messages['ATTENTION'])
