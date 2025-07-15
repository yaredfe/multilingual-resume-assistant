import os
import json
import spacy
from parser_helpers import extract_email, extract_phone, extract_education, extract_experience, extract_skills

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    print("SUCCESS: spaCy model loaded successfully")
except Exception as e:
    print(f"ERROR: Error loading spaCy model: {e}")
    nlp = None

RESUME_DIR = "data/resumes"
TRANSLATED_DIR = "data/translated"
OUTPUT_DIR = "data/parsed"

def parse_resume(text):
    """Parse resume text and extract structured information"""
    if nlp is None:
        print("ERROR: spaCy model not available, using basic parsing")
        return parse_resume_basic(text)
    
    try:
        doc = nlp(text)
        
        # Extract name (first entity that looks like a person)
        name = None
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break
        
        parsed = {
            "name": name,
            "email": extract_email(text),
            "phone": extract_phone(text),
            "education": extract_education(text),
            "experience": extract_experience(text),
            "skills": extract_skills(text),
            "text": text  # Keep original text for vector storage
        }
        return parsed
    except Exception as e:
        print(f"ERROR: Error parsing with spaCy: {e}")
        return parse_resume_basic(text)

def parse_resume_basic(text):
    """Basic parsing without spaCy"""
    parsed = {
        "name": None,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "skills": extract_skills(text),
        "text": text
    }
    return parsed

def process_directory(input_dir, output_dir):
    """Process all resume files in a directory"""
    if not os.path.exists(input_dir):
        print(f"ERROR: Input directory not found: {input_dir}")
        return 0, 0
    
    os.makedirs(output_dir, exist_ok=True)
    
    processed_count = 0
    error_count = 0
    
    for filename in os.listdir(input_dir):
        if not filename.endswith(".txt"):
            continue
            
        input_path = os.path.join(input_dir, filename)
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()

            parsed = parse_resume(text)

            # Create output filename
            if filename.endswith("_translated.txt"):
                out_filename = filename.replace("_translated.txt", ".json")
            else:
                out_filename = filename.replace(".txt", ".json")
            
            out_path = os.path.join(output_dir, out_filename)
            
            with open(out_path, 'w', encoding='utf-8') as out_f:
                json.dump(parsed, out_f, indent=2, ensure_ascii=False)

            processed_count += 1
            print(f"SUCCESS: Parsed: {filename}")
            
        except Exception as e:
            error_count += 1
            print(f"ERROR: Error parsing {filename}: {e}")

    return processed_count, error_count

def main():
    """Main function to parse resumes from both original and translated directories"""
    print("Starting resume parsing...")
    
    total_processed = 0
    total_errors = 0
    
    # Process original resumes
    print(f"\nProcessing original resumes from: {RESUME_DIR}")
    processed, errors = process_directory(RESUME_DIR, OUTPUT_DIR)
    total_processed += processed
    total_errors += errors
    
    # Process translated resumes
    print(f"\nProcessing translated resumes from: {TRANSLATED_DIR}")
    processed, errors = process_directory(TRANSLATED_DIR, OUTPUT_DIR)
    total_processed += processed
    total_errors += errors
    
    print(f"\nParsing Summary:")
    print(f"   Processed: {total_processed} resumes")
    print(f"   Errors: {total_errors}")
    print(f"   Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
