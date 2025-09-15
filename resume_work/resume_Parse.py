import os
import fitz  # PyMuPDF
import re
import sys
from pathlib import Path
import pandas as pd

# --- 🔧 Fix: Add current directory to path so 'config.py' is importable ---
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from config import get_save_directory
except ImportError as e:
    def get_save_directory():
        """Fallback: Return default directory if config is missing."""
        print("⚠️ config.py not found. Using default 'uploads/resumes' folder.")
        return str(current_dir.parent / "uploads" / "resumes")
    print(f"⚠️ Could not import config: {e}")

# --- Resume Parser Class ---


class ResumeParser:
    
    def __init__(self, save_dir=None, output_file="candidates.csv"):
        self.save_dir = save_dir or get_save_directory()
        self.excel_file = os.path.join(self.save_dir, output_file)
        self.data = []

    def extract_text_from_pdf(self, file_path):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def normalize_phone(self, num):
        digits = re.sub(r'\D', '', num)
        if digits.startswith("977") and len(digits) == 13:
            return "+977" + digits[3:]
        elif len(digits) == 10:
            return digits
        return None

    def parse_pdfs(self):
        self.data = []  # Reset data to avoid duplication on multiple calls
        
        def extract_emails(text):
            return re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)


        def extract_linkedin(text):
            # Match URL
            url_match = re.search(r'https?://(?:www\.)?linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
            if url_match:
                url = url_match.group(0)
                return url if url.startswith("http") else f"https://{url}"

            # Match partial
            partial_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
            if partial_match:
                return f"https://{partial_match.group(0)}"

            # Match "LinkedIn: username"
            handle_match = re.search(r'linkedin[^\w]*[:\s][^\w]*([\w-]{5,})', text, re.IGNORECASE)
            if handle_match:
                return f"https://linkedin.com/in/{handle_match.group(1).strip()}"
            return ""
        

        def extract_github(text):
            url_match = re.search(r'https?://(?:www\.)?github\.com/[\w-]+', text, re.IGNORECASE)
            if url_match:
                url = url_match.group(0)
                return url if url.startswith("http") else f"https://{url}"

            partial_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
            if partial_match:
                return f"https://{partial_match.group(0)}"

            handle_match = re.search(r'git(?:hub)?[^\w]*[:\s][^\w]*([\w-]{3,})', text, re.IGNORECASE)
            if handle_match:
                return f"https://github.com/{handle_match.group(1).strip()}"
            return ""
        
        for filename in os.listdir(self.save_dir):
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(self.save_dir, filename)
                try:
                    text = self.extract_text_from_pdf(file_path)

                    # Extract Email
                    # emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)

                    # Extract Phone
                    phone_raw = re.findall(r'(\+?977\d{10}|\b\d{10}\b)', text)
                    phones = [self.normalize_phone(p) for p in phone_raw if self.normalize_phone(p)]
                    linkedin = extract_linkedin(text) or "Unknown"
                    github = extract_github(text) or "Unknown"
                    email = extract_emails(text) or "Unknown"

                    # Extract Name
                    name = None
                    for line in text.splitlines():
                        if 'name' in line.lower():
                            name = line.split(":")[-1].strip()
                            break
                    if not name:
                        for line in text.splitlines():
                            if line.strip():
                                name = line.strip()
                                break


                    self.data.append({
                        "Name": name or "Unknown",
                        # "Email": ','.join(emails),
                        "Email" : ',  '.join(email),
                        "Phone": ',  '.join(phones),
                        "LinkedIn" : linkedin,
                        "GitHub" : github,
                        "FileName": filename

                    })
                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")

        print(f"📄 Parsed {len(self.data)} resumes.")


    def display_data(self):
        """Display parsed data in terminal."""
        if not self.data:
            print("⚠️ No data to display. Run parse_pdfs() first.")
            return
        df = pd.DataFrame(self.data)
        print("\n📋 Parsed Resume Data:")
        print(df.to_string(index=False))

    def save_to_excel(self):
        if not self.data:
            print("⚠️ No data to save.")
            return

        df = pd.DataFrame(self.data)

        # Detect file type and save accordingly
        ext = os.path.splitext(self.excel_file)[1].lower()

        if ext == ".xlsx" or ext == ".xls":
            df.to_excel(self.excel_file, index=False)
            print(f"✅ Saved data to Excel: {self.excel_file}")
        elif ext == ".csv":
            df.to_csv(self.excel_file, index=False)
            print(f"✅ Saved data to CSV: {self.excel_file}")
        else:
            raise ValueError(f"Unsupported file extension: {ext}. Use .csv or .xlsx")    


# --------------------------------------------------
# This block runs only when script is executed directly
# --------------------------------------------------
if __name__ == "__main__":
    parser = ResumeParser()
    parser.parse_pdfs()
    parser.display_data()  # Show results in terminal
    parser.save_to_excel()