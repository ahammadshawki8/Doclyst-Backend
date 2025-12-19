import re
from typing import List, Dict, Any

# Common medical test patterns with their normal ranges
KNOWN_TESTS = {
    'hemoglobin': {'aliases': ['hb', 'hgb', 'haemoglobin'], 'unit': 'g/dL', 'min': 12.0, 'max': 17.5},
    'wbc': {'aliases': ['white blood cell', 'leucocyte', 'wbc count'], 'unit': '/µL', 'min': 4000, 'max': 11000},
    'rbc': {'aliases': ['red blood cell', 'erythrocyte', 'rbc count'], 'unit': 'million/µL', 'min': 4.5, 'max': 5.5},
    'platelet': {'aliases': ['plt', 'platelet count', 'thrombocyte'], 'unit': '/µL', 'min': 150000, 'max': 400000},
    'hematocrit': {'aliases': ['hct', 'pcv'], 'unit': '%', 'min': 36, 'max': 50},
    'mcv': {'aliases': ['mean corpuscular volume'], 'unit': 'fL', 'min': 80, 'max': 100},
    'mch': {'aliases': ['mean corpuscular hemoglobin'], 'unit': 'pg', 'min': 27, 'max': 33},
    'mchc': {'aliases': ['mean corpuscular hemoglobin concentration'], 'unit': 'g/dL', 'min': 32, 'max': 36},
    'glucose': {'aliases': ['blood sugar', 'fasting glucose', 'fbs'], 'unit': 'mg/dL', 'min': 70, 'max': 100},
    'creatinine': {'aliases': ['serum creatinine'], 'unit': 'mg/dL', 'min': 0.7, 'max': 1.3},
    'urea': {'aliases': ['blood urea', 'bun'], 'unit': 'mg/dL', 'min': 7, 'max': 20},
    'cholesterol': {'aliases': ['total cholesterol'], 'unit': 'mg/dL', 'min': 0, 'max': 200},
    'triglycerides': {'aliases': ['tg'], 'unit': 'mg/dL', 'min': 0, 'max': 150},
    'hdl': {'aliases': ['hdl cholesterol', 'good cholesterol'], 'unit': 'mg/dL', 'min': 40, 'max': 60},
    'ldl': {'aliases': ['ldl cholesterol', 'bad cholesterol'], 'unit': 'mg/dL', 'min': 0, 'max': 100},
    'sgpt': {'aliases': ['alt', 'alanine transaminase'], 'unit': 'U/L', 'min': 7, 'max': 56},
    'sgot': {'aliases': ['ast', 'aspartate transaminase'], 'unit': 'U/L', 'min': 10, 'max': 40},
    'bilirubin': {'aliases': ['total bilirubin'], 'unit': 'mg/dL', 'min': 0.1, 'max': 1.2},
    'albumin': {'aliases': ['serum albumin'], 'unit': 'g/dL', 'min': 3.5, 'max': 5.0},
    'protein': {'aliases': ['total protein'], 'unit': 'g/dL', 'min': 6.0, 'max': 8.3},
    'sodium': {'aliases': ['na', 'serum sodium'], 'unit': 'mEq/L', 'min': 136, 'max': 145},
    'potassium': {'aliases': ['k', 'serum potassium'], 'unit': 'mEq/L', 'min': 3.5, 'max': 5.0},
    'calcium': {'aliases': ['ca', 'serum calcium'], 'unit': 'mg/dL', 'min': 8.5, 'max': 10.5},
    'vitamin d': {'aliases': ['vit d', '25-oh vitamin d'], 'unit': 'ng/mL', 'min': 30, 'max': 100},
    'vitamin b12': {'aliases': ['vit b12', 'cobalamin'], 'unit': 'pg/mL', 'min': 200, 'max': 900},
    'tsh': {'aliases': ['thyroid stimulating hormone'], 'unit': 'mIU/L', 'min': 0.4, 'max': 4.0},
    't3': {'aliases': ['triiodothyronine'], 'unit': 'ng/dL', 'min': 80, 'max': 200},
    't4': {'aliases': ['thyroxine'], 'unit': 'µg/dL', 'min': 5.0, 'max': 12.0},
    'esr': {'aliases': ['erythrocyte sedimentation rate'], 'unit': 'mm/hr', 'min': 0, 'max': 20},
    'crp': {'aliases': ['c-reactive protein'], 'unit': 'mg/L', 'min': 0, 'max': 10},
    'hba1c': {'aliases': ['glycated hemoglobin', 'a1c'], 'unit': '%', 'min': 4.0, 'max': 5.6},
    'iron': {'aliases': ['serum iron'], 'unit': 'µg/dL', 'min': 60, 'max': 170},
    'ferritin': {'aliases': ['serum ferritin'], 'unit': 'ng/mL', 'min': 12, 'max': 300},
}

def parse_medical_text(text: str) -> List[Dict[str, Any]]:
    """
    Parse OCR text and extract structured medical test data.
    Uses regex and known patterns - NO AI involved.
    """
    results = []
    text_lower = text.lower()
    
    for test_name, test_info in KNOWN_TESTS.items():
        # Build pattern to match test name and its aliases
        all_names = [test_name] + test_info['aliases']
        
        for name in all_names:
            # Pattern: test_name followed by value (with optional unit and range)
            # Example: "Hemoglobin 14.2 g/dL (12-16)" or "HB: 14.2"
            pattern = rf'{re.escape(name)}[:\s]+(\d+\.?\d*)'
            match = re.search(pattern, text_lower)
            
            if match:
                value = float(match.group(1))
                
                # Try to extract range from text
                range_pattern = rf'{re.escape(name)}.*?(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)'
                range_match = re.search(range_pattern, text_lower)
                
                if range_match:
                    min_val = float(range_match.group(1))
                    max_val = float(range_match.group(2))
                else:
                    min_val = test_info['min']
                    max_val = test_info['max']
                
                results.append({
                    'test': test_name.title(),
                    'value': value,
                    'unit': test_info['unit'],
                    'min': min_val,
                    'max': max_val,
                    'value_str': f"{value} {test_info['unit']}",
                    'range_str': f"{min_val} - {max_val}"
                })
                break  # Found this test, move to next
    
    return results

def format_for_frontend(parsed_tests: List[Dict[str, Any]], explanations: Dict[str, str]) -> List[Dict[str, str]]:
    """Format parsed tests for frontend consumption."""
    formatted = []
    
    for test in parsed_tests:
        test_name = test['test']
        formatted.append({
            'name': test_name,
            'value': test['value_str'],
            'range': test['range_str'],
            'explanation': explanations.get(test_name, 'This test measures an important health marker.'),
            'status': get_test_status(test['value'], test['min'], test['max'])
        })
    
    return formatted

def get_test_status(value: float, min_val: float, max_val: float) -> str:
    """Determine test status based on value vs range."""
    if value < min_val or value > max_val:
        # Check if significantly out of range
        if value < min_val * 0.8 or value > max_val * 1.2:
            return 'alert'
        return 'warning'
    return 'normal'
