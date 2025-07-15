import os
import json
import logging
from transformers.pipelines import pipeline
from transformers import T5Tokenizer, AutoModelForSeq2SeqLM
import torch
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Configuration ===
MATCH_RESULTS_DIR = "data/match_results"
OUTPUT_DIR = "data/interview_questions"
MODEL_DIR = "models/flan-t5-base"  # local model path

# Global generator instance
_generator = None

# === Load local model ===
def load_generator():
    """Load the text generation model with comprehensive error handling"""
    global _generator
    
    if _generator is not None:
        return _generator
    
    try:
        # Check if model directory exists
        if not os.path.exists(MODEL_DIR):
            logger.error(f"Model directory does not exist: {MODEL_DIR}")
            logger.error(f"CWD: {os.getcwd()}")
            logger.error(f"App dir contents: {os.listdir('.')}")
            return None
        
        # Check if model files exist
        required_files = ["config.json", "pytorch_model.bin", "spiece.model"]
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(MODEL_DIR, f))]
        
        if missing_files:
            logger.error(f"Missing model files: {missing_files}")
            logger.error(f"Model dir contents: {os.listdir(MODEL_DIR)}")
            return None
        
        logger.info(f"Loading model from: {MODEL_DIR}")
        logger.info(f"Model dir contents: {os.listdir(MODEL_DIR)}")
        logger.info(f"CWD: {os.getcwd()}")
        
        # Load model and tokenizer separately for better error handling
        tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)
        
        # Create pipeline
        _generator = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=256,
            device="cpu"  # Force CPU to avoid CUDA issues
        )
        
        logger.info("SUCCESS: Interview question generator loaded successfully")
        return _generator
        
    except Exception as e:
        logger.error(f"ERROR: Error loading generator: {e}")
        logger.error(f"Model path: {MODEL_DIR}")
        logger.error(f"Current working directory: {os.getcwd()}")
        if os.path.exists(MODEL_DIR):
            logger.error(f"Model directory contents: {os.listdir(MODEL_DIR)}")
        logger.error("Full exception traceback:")
        traceback.print_exc()
        return None

# === Prompt template ===
QUESTION_PROMPT_TEMPLATE = (
    "You are an AI interview assistant. Given the job title '{job_title}' and the following resume:\n\n"
    "{resume_snippet}\n\n"
    "Generate 3 relevant and specific interview questions for this job-resume match. "
    "Focus on technical skills, experience, and cultural fit. Format as a simple list."
)

def generate_interview_questions(job_title, resume_snippet, generator=None):
    """Generate interview questions for a specific job-resume match"""
    global _generator
    
    if generator is None:
        generator = _generator or load_generator()
        if generator is None:
            logger.error("Could not load question generator model")
            return "Error: Could not load question generator model. Please check if the model files are properly installed."
    
    try:
        # Validate inputs
        if not job_title or not resume_snippet:
            return "Error: Job title and resume snippet are required"
        
        # Truncate resume snippet if too long
        max_length = 1000
        if len(resume_snippet) > max_length:
            resume_snippet = resume_snippet[:max_length] + "..."
        
        prompt = QUESTION_PROMPT_TEMPLATE.format(
            job_title=job_title,
            resume_snippet=resume_snippet
        )
        
        logger.info(f"Generating questions for job: {job_title}")
        
        # Generate with error handling
        with torch.no_grad():
            output = generator(prompt, max_length=512, do_sample=True, temperature=0.7)
        
        if output and len(output) > 0:
            generated_text = output[0]["generated_text"]
            logger.info("Questions generated successfully")
            return generated_text.strip()
        else:
            logger.warning("No output generated from model")
            return "Error: No questions generated. Please try again."
        
    except Exception as e:
        logger.error(f"ERROR: Error generating questions: {e}")
        return f"Error generating questions: {str(e)}"

# === Main processing ===
def main():
    """Main function to process match results and generate interview questions"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    generator = load_generator()
    if generator is None:
        logger.error("Cannot proceed without generator model")
        return

    processed_count = 0
    error_count = 0

    for filename in os.listdir(MATCH_RESULTS_DIR):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(MATCH_RESULTS_DIR, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                match_data_list = json.load(f)
        except Exception as e:
            logger.error(f"ERROR: Error reading {filename}: {e}")
            error_count += 1
            continue

        job_title = filename.replace(".json", "").replace("_", " ")
        output_data = []

        for match in match_data_list:
            resume_text = match.get("resume_snippet", "").strip()
            if not resume_text:
                continue

            try:
                questions = generate_interview_questions(job_title, resume_text, generator)
                output_data.append({
                    "job_title": job_title,
                    "resume_snippet": resume_text,
                    "interview_questions": questions
                })
                logger.info(f"SUCCESS: Generated questions for: {job_title}")
            except Exception as e:
                logger.error(f"ERROR: Error generating questions for {job_title}: {e}")
                error_count += 1
                continue

        # Save generated questions
        if output_data:
            output_path = os.path.join(OUTPUT_DIR, filename)
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                logger.info(f"💾 Saved: {output_path}")
                processed_count += 1
            except Exception as e:
                logger.error(f"ERROR: Failed to save {output_path}: {e}")
                error_count += 1

    logger.info(f"\n Summary: Processed {processed_count} files, {error_count} errors")

if __name__ == "__main__":
    main()
