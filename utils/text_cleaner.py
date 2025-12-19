import re

def clean_ocr_text(text: str) -> str:
    """Clean OCR text - remove HTML/markdown, extract plain text."""
    if not text:
        return ""
    
    # Remove image tags
    text = re.sub(r'<img[^>]*>', '', text)
    
    # Remove div tags but keep content
    text = re.sub(r'<div[^>]*>', '', text)
    text = re.sub(r'</div>', '', text)
    
    # Extract text from table cells
    text = re.sub(r"<td[^>]*style='text-align:[^']*'>([^<]*)</td>", r'\1 ', text)
    text = re.sub(r'<td[^>]*>([^<]*)</td>', r'\1 ', text)
    text = re.sub(r'<tr[^>]*>', '\n', text)
    text = re.sub(r'</tr>', '', text)
    text = re.sub(r'<table[^>]*>', '', text)
    text = re.sub(r'</table>', '', text)
    text = re.sub(r'<thead[^>]*>.*?</thead>', '', text, flags=re.DOTALL)
    text = re.sub(r'<tbody[^>]*>', '', text)
    text = re.sub(r'</tbody>', '', text)
    text = re.sub(r'<th[^>]*>([^<]*)</th>', r'\1 ', text)
    
    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove markdown headers
    text = re.sub(r'#{1,6}\s*', '', text)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # italic
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)  # images
    text = re.sub(r'\[[^\]]*\]\([^)]*\)', '', text)  # links
    
    # Remove URLs
    text = re.sub(r'https?://[^\s]+', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Split into lines and clean each
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line and len(line) > 2:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def extract_table_data(text: str) -> list:
    """Extract data rows from markdown/HTML tables."""
    rows = []
    
    # Find table rows
    tr_pattern = r'<tr[^>]*>(.*?)</tr>'
    matches = re.findall(tr_pattern, text, re.DOTALL)
    
    for match in matches:
        # Extract cell contents
        cells = re.findall(r'<td[^>]*>([^<]*)</td>', match)
        if cells:
            rows.append([c.strip() for c in cells])
    
    return rows
