import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq

# Load environment variables from the root .env
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

SYSTEM_PROMPT = """You are an expert resume parser. You will be provided with the raw text extracted from a student's LinkedIn profile PDF or resume.
Your task is to parse this text and structure it into a clean JSON object that maps perfectly to the fields required by the Handshake profile platform.

Output MUST be a single valid JSON object. Do not include markdown code block styling (like ```json), do not include extra explanations, and do not wrap it. Only return the raw JSON string starting with '{' and ending with '}'.

Here is the exact JSON structure and expected formats for each field:

{
  "summary": "A concise professional bio or about summary (string or null).",
  "education": [
    {
      "school": "Full name of the university or college (string).",
      "degree": "Degree name, e.g., 'Bachelor of Science', 'Master of Science' (string).",
      "major": "Major or field of study, e.g., 'Computer Science' (string).",
      "gpa": "GPA as a string, e.g., '3.82' (string or null).",
      "start_month": "Starting month, e.g., 'September' (string).",
      "start_year": "Starting year, e.g., '2022' (string).",
      "end_month": "Graduation/end month, e.g., 'May' (string).",
      "end_year": "Graduation/end year, e.g., '2026' (string).",
      "is_current": true/false (boolean)
    }
  ],
  "experience": [
    {
      "employer": "Name of the employer/company (string).",
      "role": "Job title or role, e.g., 'Software Engineer Intern' (string).",
      "location": "City, State or 'Remote' (string).",
      "start_month": "Starting month, e.g., 'June' (string).",
      "start_year": "Starting year, e.g., '2024' (string).",
      "end_month": "End month, e.g., 'August' or null if current (string or null).",
      "end_year": "End year, e.g., '2024' or null if current (string or null).",
      "is_current": true/false (boolean),
      "description": "A bulleted or detailed description of responsibilities and accomplishments (string)."
    }
  ],
  "projects": [
    {
      "title": "Project name (string).",
      "start_month": "Starting month (string or null).",
      "start_year": "Starting year (string or null).",
      "end_month": "End month or null (string or null).",
      "end_year": "End year or null (string or null).",
      "is_current": true/false (boolean),
      "description": "Description of what was built and technologies used (string).",
      "url": "Project URL or GitHub link if present (string or null)"
    }
  ],
  "organizations": [
    {
      "organization": "Club, team, or student organization name (string).",
      "role": "Role or position, e.g., 'Treasurer' (string).",
      "start_month": "Starting month (string).",
      "start_year": "Starting year (string).",
      "end_month": "End month or null (string or null).",
      "end_year": "End year or null (string or null).",
      "is_current": true/false (boolean),
      "description": "Description of activities or duties (string)."
    }
  ],
  "skills": [
    "List of programming languages, tools, frameworks, and professional skills as individual strings"
  ]
}

Double check that:
1. Dates (months and years) are spelled out correctly (e.g. "September" not "Sep" or "09", "2024" not "24").
2. Standardized degrees are identified clearly (e.g., "Bachelor of Science", "Bachelor of Arts").
3. If end dates are 'Present' or empty and is_current is true, set the end month and end year to null.
4. Ensure descriptions capture key bullet points.
"""

def extract_text_from_pdf(pdf_path: Path) -> str:
    print(f"[*] Reading PDF file: {pdf_path}")
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
    
    reader = PdfReader(pdf_path)
    text_content = []
    
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text_content.append(f"--- Page {i+1} ---\n{page_text}")
            
    return "\n\n".join(text_content)

def parse_profile(pdf_path: Path, output_json_path: Path) -> dict:
    # 1. Extract text
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text.strip():
        raise ValueError("Could not extract any text from the provided PDF file.")
        
    print(f"[+] Extracted {len(raw_text)} characters of text from PDF.")
    
    # 2. Get API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file or environment.")
        
    # 3. Request parsing via Groq
    print("[*] Contacting Groq LLM API (llama-3.3-70b-versatile) for resume parsing...")
    client = Groq(api_key=api_key)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the LinkedIn profile text:\n\n{text_content_placeholder}\n{raw_text}"} if False else {"role": "user", "content": f"Here is the LinkedIn profile text:\n\n{raw_text}"}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    
    raw_json = response.choices[0].message.content.strip()
    parsed_data = json.loads(raw_json)
    
    # 4. Save JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2)
        
    print(f"[+] Saved structured profile details to: {output_json_path}")
    return parsed_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser.py <path_to_pdf>")
        sys.exit(1)
        
    pdf_file = Path(sys.argv[1])
    output_file = Path(__file__).parent / "profile.json"
    
    try:
        data = parse_profile(pdf_file, output_file)
        print("\n--- Parsed Profile Summary ---")
        print(f"Summary: {data.get('summary', 'None')}")
        print(f"Education Count: {len(data.get('education', []))}")
        print(f"Experience Count: {len(data.get('experience', []))}")
        print(f"Projects Count: {len(data.get('projects', []))}")
        print(f"Organizations Count: {len(data.get('organizations', []))}")
        print(f"Skills: {', '.join(data.get('skills', []))}")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
