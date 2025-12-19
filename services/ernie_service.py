import json
import requests
from typing import Dict, Any
from config import Config

MEDICAL_PROMPT = """You are Doclyst, a friendly medical report assistant. Analyze this medical report and explain it in simple terms.

RULES:
1. Identify the report type (blood test, X-ray, ECG, etc.)
2. Extract ALL test results with their values and normal ranges
3. For each test, determine if it's normal, low, or high
4. Explain each finding in simple language (5th grade reading level)
5. Be calm and reassuring
6. Do NOT diagnose any disease
7. Do NOT recommend specific treatments
8. Suggest consulting a doctor for abnormal values

MEDICAL REPORT:
{report_text}

Respond with ONLY valid JSON (no markdown):
{{"reportType":"type","overallStatus":"NORMAL/ATTENTION/URGENT","summary":"friendly summary","findings":[{{"name":"test name","value":"result","range":"normal range","explanation":"simple explanation","status":"normal/warning/alert"}}]}}"""

def call_groq(prompt: str) -> str:
    """PRIMARY: Call Groq API (fast, free)."""
    api_key = Config.GROQ_API_KEY
    if not api_key:
        print("[LLM] No GROQ_API_KEY")
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
        print("[LLM] Using Groq (primary)...")
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

def call_ernie(prompt: str) -> str:
    """FALLBACK: Call ERNIE via AI Studio API (sponsor)."""
    api_key = Config.ERNIE_ACCESS_TOKEN
    if not api_key:
        print("[LLM] No ERNIE_ACCESS_TOKEN")
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
        print("[LLM] Using ERNIE (sponsor fallback)...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.ok:
            text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            if text:
                print(f"[LLM] ERNIE success: {len(text)} chars")
                return text
        print(f"[LLM] ERNIE error: {response.status_code}")
    except Exception as e:
        print(f"[LLM] ERNIE exception: {e}")
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

def analyze_medical_report(report_text: str) -> Dict[str, Any]:
    """Analyze medical report using LLM."""
    
    print(f"[ANALYSIS] Processing {len(report_text)} chars...")
    prompt = MEDICAL_PROMPT.format(report_text=report_text[:8000])
    
    # Primary: Groq
    response = call_groq(prompt)
    if response:
        result = parse_json_response(response)
        if result and result.get("findings"):
            print(f"[LLM] Analysis complete: {result.get('reportType')}")
            return result
    
    # Fallback: ERNIE (sponsor)
    response = call_ernie(prompt)
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
        }]
    }
