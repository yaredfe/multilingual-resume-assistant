#!/usr/bin/env python3
"""
Data Setup Script for Multilingual Resume Screener
Automates the data preparation pipeline
"""

import os
import sys
import subprocess
from pathlib import Path

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{description}...")
    print(f"   Running: python Scripts/{script_name}")
    
    try:
        result = subprocess.run(
            [sys.executable, f"Scripts/{script_name}"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print(f"SUCCESS: {description} completed successfully")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"ERROR: {description} failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"ERROR: Error running {script_name}: {e}")
        return False
    
    return True

def check_prerequisites():
    """Check if prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check if CSV files exist
    csv_files = ["data/resumes.csv", "data/aug_train.csv"]
    missing_files = []
    
    for file_path in csv_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("ERROR: Missing CSV files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nPlease ensure the CSV files are in the data/ directory")
        return False
    
    print("SUCCESS: Prerequisites check passed")
    return True

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = [
        "data/resumes",
        "data/translated", 
        "data/parsed",
        "data/chroma_db",
        "data/job_descriptions",
        "data/match_results",
        "data/interview_questions"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   SUCCESS: Created: {directory}")
    
    print("SUCCESS: All directories created")

def main():
    """Main setup function"""
    print("=" * 60)
    print("Multilingual Resume Screener - Data Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("Scripts"):
        print("ERROR: Please run this script from the project root directory")
        sys.exit(1)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Run setup scripts in order
    setup_steps = [
        ("split_resumes.py", "Splitting resumes from CSV"),
        ("translate_resumes.py", "Translating non-English resumes"),
        ("parse_resumes.py", "Parsing resume data"),
        ("vector_store.py", "Building vector database"),
        ("generate_jds_from_hr_dataset.py", "Generating job descriptions"),
        ("semantic_matching.py", "Running semantic matching"),
        ("interview_question_generator.py", "Generating interview questions")
    ]
    
    success_count = 0
    total_steps = len(setup_steps)
    
    for script_name, description in setup_steps:
        if run_script(script_name, description):
            success_count += 1
        else:
            print(f"WARNING: Skipping remaining steps due to failure in {script_name}")
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("Setup Summary")
    print("=" * 60)
    print(f"SUCCESS: Completed: {success_count}/{total_steps} steps")
    
    if success_count == total_steps:
        print("\nSUCCESS: Data setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the application: python run.py")
        print("2. Open your browser to: http://localhost:8000")
        print("3. Start screening resumes!")
    else:
        print(f"\nWARNING: Setup completed with {total_steps - success_count} failures")
        print("Please check the error messages above and fix any issues")

if __name__ == "__main__":
    main() 