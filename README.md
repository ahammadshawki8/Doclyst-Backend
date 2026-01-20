# 🏥 Doclyst Backend

A Flask-powered medical report analysis API that transforms complex medical documents into patient-friendly explanations.

## ✨ Overview

Doclyst Backend processes medical reports (blood tests, X-rays, ECGs) and returns clear, simple explanations that anyone can understand—without providing medical advice or diagnoses.

| Input | Output |
|-------|--------|
| Medical report (PDF/PNG/JPG) | Simple explanation + urgency indicator + disclaimer |

## 🛠️ Tech Stack

- **PaddleOCR** — OCR text extraction
- **OCR Space** — Alternative OCR service
- **ERNIE** — Large language model for analysis
- **Groq** — LLM inference
- **Flask** — Python web framework

## 🏗️ Architecture

```
┌─────────────────┐
│  Medical Report │  (PDF / PNG / JPG)
└────────┬────────┘
         ▼
┌─────────────────┐
│   Flask API     │  POST /analyze
└────────┬────────┘
         ▼
┌─────────────────┐
│  🔤 PaddleOCR   │  Text Extraction
└────────┬────────┘
         ▼
┌─────────────────┐
│   🧠 ERNIE      │  Medical Explanation
└────────┬────────┘
         ▼
┌─────────────────┐
│  JSON Response  │  Status + Summary + Findings
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone and navigate
cd Doclyst-Backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
```

**Environment Variables:**
| Variable | Description |
|----------|-------------|
| `ERNIE_ACCESS_TOKEN` | ERNIE API token |
| `GROQ_API_KEY` | Groq LLM API key |

### Run Server

```bash
# Development
python app.py

# Production
gunicorn app:app
```

Server runs at `http://localhost:5000`

## 📡 API Reference

### `POST /analyze`

Analyze one or more medical report files.

**Request:**
```
Content-Type: multipart/form-data
Field: file (supports multiple files)
```

**Response:**
```json
{
  "overallStatus": "ATTENTION",
  "summary": "Most of your results look good. A few values need attention.",
  "tests": [
    {
      "name": "Hemoglobin",
      "value": "10.2 g/dL",
      "range": "12.0 - 17.5 g/dL",
      "explanation": "Your hemoglobin is slightly below the typical range, which may cause tiredness.",
      "status": "warning"
    }
  ],
  "disclaimer": "Doclyst does not provide medical advice. This explanation is for understanding only."
}
```

**Status Levels:**
| Status | Meaning |
|--------|---------|
| `NORMAL` | All values within expected range |
| `ATTENTION` | Some values need monitoring |
| `URGENT` | Consult a doctor promptly |

### `GET /health`

Health check endpoint.

```json
{"status": "healthy", "service": "doclyst-backend"}
```

## 📁 Project Structure

```
Doclyst-Backend/
├── app.py                  # Flask application entry
├── config.py               # Configuration management
├── routes/
│   └── analyze.py          # API endpoints
├── services/
│   ├── ocr_service.py      # OCR integration
│   ├── ernie_service.py    # LLM integration
│   ├── medical_parser.py   # Data structuring
│   └── risk_engine.py      # Urgency assessment
├── utils/
│   ├── file_utils.py       # File handling
│   └── text_cleaner.py     # Text normalization
├── requirements.txt
└── README.md
```

## 🧪 Supported Reports

| Type | Support |
|------|---------|
| Blood Tests (CBC) | ✅ Full analysis |
| Biochemistry Panels | ✅ Full analysis |
| ECG Reports | ✅ Full analysis |
| X-ray Reports | ✅ Full analysis |
| ECG Images | ✅ Description only |
| X-ray Images | ✅ Description only |

## 🔒 Safety & Compliance

Doclyst prioritizes patient safety:

- **Explanation, not diagnosis** — We clarify results, never diagnose conditions
- **Clear disclaimers** — Every response includes a medical disclaimer
- **No data storage** — Reports are processed and immediately discarded
- **No personalization** — Analysis is based solely on report content

> *"We help patients understand, not decide."*

## 🧪 Testing

```bash
# Test with cURL
curl -X POST http://localhost:5000/analyze \
  -F "file=@your_report.jpg"

# Test multiple files
curl -X POST http://localhost:5000/analyze \
  -F "file=@page1.jpg" \
  -F "file=@page2.jpg"
```

## 🚢 Deployment

### Render (Recommended)

1. Push to GitHub
2. Connect repo on [render.com](https://render.com)
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Add environment variables

## 📄 License

MIT License
