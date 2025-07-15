import os
from tqdm import tqdm
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect
import glob

# Local model paths
MODEL_DIR = os.path.join(os.getcwd(), "models")
LANG_TO_MODEL = {
    "fr": os.path.join(MODEL_DIR, "opus-mt-fr-en"),
    "es": os.path.join(MODEL_DIR, "opus-mt-es-en"),
    "de": os.path.join(MODEL_DIR, "opus-mt-de-en"),
}

def detect_language(text):
    """Detect the language of the input text"""
    try:
        return detect(text)
    except Exception as e:
        print(f"ERROR: Error detecting language: {e}")
        return "unknown"

def load_model_tokenizer(lang_code):
    """Load the translation model and tokenizer for a specific language"""
    model_path = LANG_TO_MODEL.get(lang_code)
    if model_path is None or not os.path.isdir(model_path):
        raise ValueError(f"No local model found for language code '{lang_code}'")

    try:
        tokenizer = MarianTokenizer.from_pretrained(model_path)
        model = MarianMTModel.from_pretrained(model_path)
        print(f"SUCCESS: Loaded translation model for {lang_code}")
        return model, tokenizer
    except Exception as e:
        print(f"ERROR: Error loading model for {lang_code}: {e}")
        raise

def translate_text(text, lang_code):
    """Translate text from the specified language to English"""
    try:
        model, tokenizer = load_model_tokenizer(lang_code)
        
        # Prepare the text for translation
        batch = tokenizer.prepare_seq2seq_batch([text], return_tensors="pt")
        
        # Generate translation
        generated = model.generate(**batch)
        translated = tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        
        return translated
    except Exception as e:
        print(f"ERROR: Error translating text: {e}")
        return text  # Return original text if translation fails

def process_resumes(input_dir="data/resumes", output_dir="data/translated"):
    """Process resumes in the input directory and translate non-English ones"""
    os.makedirs(output_dir, exist_ok=True)

    resume_files = glob.glob(os.path.join(input_dir, "*.txt"))
    
    if not resume_files:
        print(f"ERROR: No resume files found in {input_dir}")
        return

    translated_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in tqdm(resume_files, desc="Translating non-English resumes"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            lang = detect_language(text)
            
            if lang not in LANG_TO_MODEL:
                print(f"SKIPPING: Skipping {os.path.basename(file_path)}, unsupported language: {lang}")
                skipped_count += 1
                continue

            # Translate the text
            translated_text = translate_text(text, lang)
            
            # Save translated text
            output_path = os.path.join(output_dir, os.path.basename(file_path))
            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(translated_text)
            
            translated_count += 1
            print(f"SUCCESS: Translated {os.path.basename(file_path)} ({lang} -> en)")
            
        except Exception as e:
            print(f"ERROR: Error processing {os.path.basename(file_path)}: {e}")
            error_count += 1

    print(f"\nTranslation Summary:")
    print(f"   Translated: {translated_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Errors: {error_count}")

def translate_single_resume(text, lang_code=None):
    """Translate a single resume text"""
    if lang_code is None:
        lang_code = detect_language(text)
    
    if lang_code not in LANG_TO_MODEL:
        return text, lang_code  # Return original if language not supported
    
    translated_text = translate_text(text, lang_code)
    return translated_text, lang_code

if __name__ == "__main__":
    process_resumes()
