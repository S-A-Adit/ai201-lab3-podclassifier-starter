import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure the local directory is in the path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from parser import parse_profile
    from filler import run_filler
except ImportError as e:
    print(f"[!] Import error: {e}")
    print("    Make sure you run the script from the directory containing parser.py and filler.py.")
    sys.exit(1)

def main():
    print("==========================================================")
    print("   LinkedIn Profile PDF to Handshake Profile Autofiller   ")
    print("==========================================================")
    
    # 1. Load environment and verify Groq key
    ROOT_DIR = Path(__file__).parent.parent
    load_dotenv(ROOT_DIR / ".env")
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("[!] Error: GROQ_API_KEY is not defined in your .env file.")
        print(f"    Please check the .env file in the directory: {ROOT_DIR}")
        sys.exit(1)
        
    # 2. Get PDF path
    pdf_path_str = ""
    if len(sys.argv) > 1:
        pdf_path_str = sys.argv[1]
    else:
        pdf_path_str = input("[*] Enter the path to your LinkedIn profile PDF (e.g. resume.pdf): ").strip()
        
    if not pdf_path_str:
        print("[!] Error: No PDF path provided. Exiting.")
        sys.exit(1)
        
    pdf_path = Path(pdf_path_str)
    if not pdf_path.exists():
        print(f"[!] Error: File does not exist at '{pdf_path.resolve()}'")
        sys.exit(1)
        
    output_json = Path(__file__).parent / "profile.json"
    
    # 3. Parse PDF
    print("\n--- STEP 1: Parsing LinkedIn Profile PDF ---")
    try:
        parse_profile(pdf_path, output_json)
        print("[+] PDF parsing completed successfully.")
    except Exception as e:
        print(f"[!] Error during parsing: {e}")
        sys.exit(1)
        
    # 4. Fill Handshake
    print("\n--- STEP 2: Autofilling Handshake Profile ---")
    try:
        run_filler()
    except Exception as e:
        print(f"[!] Error during Handshake autofill: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
