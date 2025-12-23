import json
import base64
import requests
from typing import Dict, Any, Optional
from config import Config

# Timeout for primary LLM (20 seconds)
PRIMARY_TIMEOUT = 20

# Language configurations
LANGUAGE_NAMES = {
    'en': 'English',
    'bn': 'Bengali (বাংলা)',
    'zh': 'Chinese (中文)',
    'hi': 'Hindi (हिन्दी)',
    'es': 'Spanish (Español)'
}

def get_language_instruction(language: str) -> str:
    """Get language instruction for prompts."""
    if language == 'en':
        return ""
    lang_name = LANGUAGE_NAMES.get(language, 'English')
    return f"\n\nIMPORTANT: Respond in {lang_name}. All text fields (summary, explanations, doesNotMean, nextSteps, doctorQuestions) MUST be written in {lang_name}. Keep test names and values in their original form, but translate all explanatory text."

MEDICAL_PROMPT = """You are Doclyst, a friendly medical report assistant. Analyze this medical report and explain it in simple terms.

RULES:
1. Identify the report type (blood test, X-ray, ECG, etc.)
2. Extract ALL test results with their values and normal ranges
3. For each test, determine if it's normal, low, or high
4. Explain each finding in simple language (5th grade reading level)
5. Be calm and reassuring - PREVENT PANIC
6. Do NOT diagnose any disease
7. Do NOT recommend specific treatments
8. Suggest consulting a doctor for abnormal values

ANTI-PANIC GUIDANCE (IMPORTANT):
- Generate "doesNotMean": 2-3 things this result does NOT mean (to prevent panic)
- Generate "nextSteps": 2-3 safe, actionable steps the patient should take
- Generate "doctorQuestions": 2-3 questions the patient can ask their doctor
{language_instruction}
MEDICAL REPORT:
{report_text}

Respond with ONLY valid JSON (no markdown):
{{"reportType":"type","overallStatus":"NORMAL/ATTENTION/URGENT","summary":"friendly summary","findings":[{{"name":"test name","value":"result","range":"normal range","explanation":"simple explanation","status":"normal/warning/alert"}}],"doesNotMean":["This does NOT mean...","..."],"nextSteps":["Step 1...","Step 2..."],"doctorQuestions":["Question 1?","Question 2?"]}}"""

# Vision prompt for ECG/X-ray images
VISION_PROMPT = """You are Doclyst, a friendly medical image assistant. Analyze this medical image and describe what you observe.

IMPORTANT RULES:
1. Identify the type of medical image (ECG, X-ray, CT scan, ultrasound, etc.)
2. Describe observable patterns, shapes, and features you can see
3. Use simple language (5th grade reading level)
4. Be calm and reassuring - PREVENT PANIC
5. Do NOT diagnose any disease or condition
6. Do NOT make definitive medical conclusions
7. Always recommend consulting a doctor for proper interpretation

For ECG images, describe:
- Heart rhythm pattern (regular/irregular)
- Wave patterns you observe
- Any notable features

For X-ray/imaging, describe:
- Body part shown
- General appearance
- Any visible patterns or areas of interest

ANTI-PANIC GUIDANCE:
- Generate "doesNotMean": 2-3 things this image does NOT indicate (to prevent panic)
- Generate "nextSteps": 2-3 safe steps the patient should take
- Generate "doctorQuestions": 2-3 questions to ask the doctor
{language_instruction}
Respond with ONLY valid JSON (no markdown):
{{"reportType":"ECG/X-ray/etc","overallStatus":"NORMAL/ATTENTION/URGENT","summary":"friendly description of what you observe","findings":[{{"name":"observation name","value":"what you see","range":"typical appearance","explanation":"simple explanation","status":"normal/warning/alert"}}],"doesNotMean":["This does NOT mean..."],"nextSteps":["Step 1..."],"doctorQuestions":["Question 1?"]}}"""

COMPARISON_PROMPT = """You are Doclyst, a medical report comparison assistant. Compare these two medical reports (OLD vs NEW) and highlight changes.

RULES:
1. Identify tests that appear in both reports
2. For each test, determine if it IMPROVED, WORSENED, or stayed STABLE
3. Identify any NEW findings in the new report
4. Explain changes in simple language (5th grade reading level)
5. Be calm and reassuring - celebrate improvements!
6. Do NOT diagnose any disease
7. Do NOT recommend specific treatments
{language_instruction}
OLD REPORT:
{old_report}

NEW REPORT:
{new_report}

Respond with ONLY valid JSON (no markdown):
{{"reportType":"type","overallStatus":"NORMAL/ATTENTION/URGENT","summary":"friendly comparison summary","findings":[{{"name":"test name","value":"new value","range":"normal range","explanation":"simple explanation","status":"normal/warning/alert"}}],"comparison":{{"improved":[{{"name":"test","oldValue":"old","newValue":"new","change":"improved","explanation":"what improved"}}],"worsened":[{{"name":"test","oldValue":"old","newValue":"new","change":"worsened","explanation":"what worsened"}}],"stable":[{{"name":"test","oldValue":"old","newValue":"new","change":"stable","explanation":"stayed same"}}],"newFindings":[{{"name":"test","oldValue":"N/A","newValue":"new","change":"new","explanation":"new finding"}}],"comparisonSummary":"overall comparison summary"}},"doesNotMean":["..."],"nextSteps":["..."],"doctorQuestions":["..."]}}"""


def encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_mime_type(image_path: str) -> str:
    """Get MIME type from image path."""
    ext = image_path.lower().split('.')[-1]
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    return mime_types.get(ext, 'image/jpeg')


def call_ernie(prompt: str) -> str:
    """PRIMARY: Call ERNIE via AI Studio API (sponsor)."""
    api_key = Config.ERNIE_ACCESS_TOKEN
    if not api_key:
        print("[LLM] No ERNIE_ACCESS_TOKEN configured")
        return ""
    
    url = "https://aistudio.baidu.com/llm/lmapi/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "ernie-4.5-8k",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        print("[LLM] Using ERNIE (primary - sponsor)...")
        response = requests.post(url, headers=headers, json=payload, timeout=PRIMARY_TIMEOUT)
        if response.ok:
            text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            if text:
                print(f"[LLM] ERNIE success: {len(text)} chars")
                return text
        print(f"[LLM] ERNIE error: {response.status_code} - {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"[LLM] ERNIE timeout after {PRIMARY_TIMEOUT}s")
    except Exception as e:
        print(f"[LLM] ERNIE exception: {e}")
    return ""


def call_ernie_vision(prompt: str, image_path: str) -> str:
    """Call ERNIE Vision model for image analysis (sponsor)."""
    api_key = Config.ERNIE_ACCESS_TOKEN
    if not api_key:
        print("[VISION] No ERNIE_ACCESS_TOKEN configured")
        return ""
    
    url = "https://aistudio.baidu.com/llm/lmapi/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Encode image
    image_base64 = encode_image_to_base64(image_path)
    mime_type = get_image_mime_type(image_path)
    
    payload = {
        "model": "ernie-4.5-8k",  # ERNIE supports vision
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}}
            ]
        }],
        "temperature": 0.3
    }
    
    try:
        print("[VISION] Using ERNIE Vision (primary - sponsor)...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.ok:
            text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            if text:
                print(f"[VISION] ERNIE Vision success: {len(text)} chars")
                return text
        print(f"[VISION] ERNIE Vision error: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"[VISION] ERNIE Vision exception: {e}")
    return ""


def call_groq(prompt: str) -> str:
    """FALLBACK: Call Groq API."""
    api_key = Config.GROQ_API_KEY
    if not api_key:
        print("[LLM] No GROQ_API_KEY configured")
        return ""
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 4096
    }
    
    try:
        print("[LLM] Using Groq (fallback)...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.ok:
            text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            if text:
                print(f"[LLM] Groq success: {len(text)} chars")
                return text
        print(f"[LLM] Groq error: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"[LLM] Groq exception: {e}")
    return ""


def call_groq_vision(prompt: str, image_path: str) -> str:
    """FALLBACK: Call Groq Vision API for image analysis."""
    api_key = Config.GROQ_API_KEY
    if not api_key:
        print("[VISION] No GROQ_API_KEY configured")
        return ""
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Encode image
    image_base64 = encode_image_to_base64(image_path)
    mime_type = get_image_mime_type(image_path)
    
    payload = {
        "model": "llama-3.2-90b-vision-preview",  # Groq vision model
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}}
            ]
        }],
        "temperature": 0.3,
        "max_tokens": 4096
    }
    
    try:
        print("[VISION] Using Groq Vision (fallback)...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.ok:
            text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            if text:
                print(f"[VISION] Groq Vision success: {len(text)} chars")
                return text
        print(f"[VISION] Groq Vision error: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"[VISION] Groq Vision exception: {e}")
    return ""


def parse_json_response(text: str) -> dict:
    """Parse JSON from LLM response."""
    if not text:
        return {}
    try:
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            for part in text.split("```"):
                if "{" in part and "}" in part:
                    text = part
                    break
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception as e:
        print(f"[JSON] Parse error: {e}")
    return {}


def analyze_medical_image(image_path: str, language: str = 'en') -> Dict[str, Any]:
    """Analyze medical image (ECG, X-ray, etc.) using vision models."""
    
    print(f"[VISION] Analyzing image: {image_path}")
    lang_instruction = get_language_instruction(language)
    prompt = VISION_PROMPT.format(language_instruction=lang_instruction)
    
    # Primary: ERNIE Vision (sponsor)
    response = call_ernie_vision(prompt, image_path)
    if response:
        result = parse_json_response(response)
        if result and result.get("findings"):
            print(f"[VISION] Analysis complete: {result.get('reportType')}")
            return result
    
    # Fallback: Groq Vision
    print("[VISION] ERNIE Vision failed, trying Groq Vision fallback...")
    response = call_groq_vision(prompt, image_path)
    if response:
        result = parse_json_response(response)
        if result and result.get("findings"):
            print(f"[VISION] Analysis complete: {result.get('reportType')}")
            return result
    
    # Last resort fallback
    print("[VISION] All vision models failed, using fallback")
    return {
        "reportType": "Medical Image",
        "overallStatus": "ATTENTION",
        "summary": "This appears to be a medical image (possibly ECG or X-ray). Please consult your doctor for proper interpretation of this image.",
        "findings": [{
            "name": "Image Analysis",
            "value": "Requires professional review",
            "range": "N/A",
            "explanation": "Medical images like ECGs and X-rays require trained professionals to interpret accurately. Please share this image with your doctor.",
            "status": "warning"
        }],
        "doesNotMean": [
            "This does NOT mean there is definitely something wrong",
            "Many medical images show normal variations",
            "Only a trained doctor can properly interpret this image"
        ],
        "nextSteps": [
            "Share this image with your doctor",
            "Ask your doctor to explain what they see",
            "Keep this image for your medical records"
        ],
        "doctorQuestions": [
            "What does this image show?",
            "Is everything normal in this image?",
            "Do I need any follow-up tests?"
        ]
    }


def analyze_medical_report(report_text: str, language: str = 'en', image_paths: Optional[list] = None) -> Dict[str, Any]:
    """Analyze medical report using ERNIE (primary) with Groq fallback.
    
    If report_text is empty/minimal but image_paths provided, uses vision analysis.
    """
    
    # If no text but images provided, use vision analysis
    if (not report_text or len(report_text.strip()) < 50) and image_paths:
        print("[ANALYSIS] No text found, using vision analysis for images...")
        # Analyze first image (typically the main report)
        return analyze_medical_image(image_paths[0], language)
    
    print(f"[ANALYSIS] Processing {len(report_text)} chars in {language}...")
    lang_instruction = get_language_instruction(language)
    prompt = MEDICAL_PROMPT.format(
        report_text=report_text[:8000],
        language_instruction=lang_instruction
    )
    
    # Primary: ERNIE (sponsor) - wait up to 20 seconds
    response = call_ernie(prompt)
    if response:
        result = parse_json_response(response)
        if result and result.get("findings"):
            print(f"[LLM] Analysis complete: {result.get('reportType')}")
            return result
    
    # Fallback: Groq
    print("[LLM] ERNIE failed, trying Groq fallback...")
    response = call_groq(prompt)
    if response:
        result = parse_json_response(response)
        if result and result.get("findings"):
            print(f"[LLM] Analysis complete: {result.get('reportType')}")
            return result
    
    # Last resort: basic fallback
    print("[LLM] All LLMs failed, using basic fallback")
    return {
        "reportType": "Medical Report",
        "overallStatus": "ATTENTION",
        "summary": "Your report has been received. Please consult your doctor for detailed interpretation.",
        "findings": [{
            "name": "Report Status",
            "value": "Received",
            "range": "N/A",
            "explanation": "The report was processed but requires professional review.",
            "status": "warning"
        }],
        "doesNotMean": [
            "This does NOT mean you have a confirmed disease",
            "Abnormal values don't always indicate serious problems",
            "Many factors can temporarily affect test results"
        ],
        "nextSteps": [
            "Schedule a follow-up with your doctor to discuss results",
            "Keep this report for your medical records",
            "Note any symptoms you've been experiencing to share with your doctor"
        ],
        "doctorQuestions": [
            "What do these results mean for my overall health?",
            "Should I repeat any tests or do additional testing?",
            "Are there lifestyle changes that could help improve these values?"
        ]
    }


def compare_medical_reports(old_report: str, new_report: str, language: str = 'en') -> Dict[str, Any]:
    """Compare two medical reports using ERNIE (primary) with Groq fallback."""
    
    print(f"[COMPARISON] Old: {len(old_report)} chars, New: {len(new_report)} chars, Lang: {language}")
    lang_instruction = get_language_instruction(language)
    prompt = COMPARISON_PROMPT.format(
        old_report=old_report[:4000],
        new_report=new_report[:4000],
        language_instruction=lang_instruction
    )
    
    # Primary: ERNIE (sponsor) - wait up to 20 seconds
    response = call_ernie(prompt)
    if response:
        result = parse_json_response(response)
        if result and result.get("comparison"):
            result["isComparison"] = True
            print("[LLM] Comparison complete")
            return result
    
    # Fallback: Groq
    print("[LLM] ERNIE failed, trying Groq fallback...")
    response = call_groq(prompt)
    if response:
        result = parse_json_response(response)
        if result and result.get("comparison"):
            result["isComparison"] = True
            print("[LLM] Comparison complete")
            return result
    
    # Fallback
    print("[LLM] Comparison failed, using fallback")
    return {
        "reportType": "Medical Report Comparison",
        "overallStatus": "ATTENTION",
        "summary": "Both reports have been received. Please consult your doctor for detailed comparison.",
        "findings": [],
        "isComparison": True,
        "comparison": {
            "improved": [],
            "worsened": [],
            "stable": [],
            "newFindings": [],
            "comparisonSummary": "Unable to automatically compare. Please review with your doctor."
        },
        "doesNotMean": [
            "Changes don't always indicate problems",
            "Some variation between tests is normal"
        ],
        "nextSteps": [
            "Discuss both reports with your doctor",
            "Ask about any significant changes"
        ],
        "doctorQuestions": [
            "How do these results compare overall?",
            "Are any changes concerning?"
        ]
    }
