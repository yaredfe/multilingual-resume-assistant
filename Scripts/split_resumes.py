#!/usr/bin/env python3
"""
Split Resumes Script for Multilingual Resume Screener
Converts CSV resume dataset into individual text files for processing
"""

import pandas as pd
import os
import sys
from pathlib import Path

# Configuration
CSV_PATH = "data/resumes.csv"
OUTPUT_FOLDER = "data/resumes"
ENCODING = "utf-8"

def detect_resume_column(df):
    """Detect the column containing resume text"""
    resume_keywords = ["resume", "text", "content", "description", "cv"]
    
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in resume_keywords):
            return col
    
    # If no obvious column found, try to find the longest text column
    text_columns = []
    for col in df.columns:
        if df[col].dtype == 'object':  # String/object columns
            avg_length = df[col].astype(str).str.len().mean()
            if avg_length > 100:  # Assume resume text is longer than 100 chars
                text_columns.append((col, avg_length))
    
    if text_columns:
        # Return the column with the longest average text
        return max(text_columns, key=lambda x: x[1])[0]
    
    return None

def clean_resume_text(text):
    """Clean and normalize resume text"""
    if pd.isna(text):
        return ""
    
    text = str(text).strip()
    
    # Remove excessive whitespace
    import re
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common CSV artifacts
    text = text.replace('\\n', '\n').replace('\\t', '\t')
    
    return text

def split_resumes(csv_path, output_folder):
    """Split CSV resumes into individual text files"""
    print(f"Loading CSV file: {csv_path}")
    
    # Check if CSV file exists
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        print("Please ensure the resumes.csv file is in the data/ directory")
        return False
    
    try:
        # Load CSV with error handling
        df = pd.read_csv(csv_path, encoding=ENCODING)
        print(f"SUCCESS: Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        
    except Exception as e:
        print(f"ERROR: Error loading CSV: {e}")
        return False
    
    # Detect resume column
    resume_column = detect_resume_column(df)
    if not resume_column:
        print("ERROR: Could not find resume text column!")
        print("Available columns:")
        for col in df.columns:
            print(f"   - {col}")
        return False
    
    print(f"Using resume column: '{resume_column}'")
    
    # Create output directory
    os.makedirs(output_folder, exist_ok=True)
    print(f"Output directory: {output_folder}")
    
    # Process each resume
    successful_exports = 0
    failed_exports = 0
    
    for idx, row in df.iterrows():
        try:
            resume_text = clean_resume_text(row[resume_column])
            
            if not resume_text:
                print(f"WARNING: Skipping row {idx+1}: Empty resume text")
                failed_exports += 1
                continue
            
            # Create filename
            filename = f"resume_{idx+1:04d}.txt"
            file_path = os.path.join(output_folder, filename)
            
            # Write resume to file
            with open(file_path, "w", encoding=ENCODING) as f:
                f.write(resume_text)
            
            successful_exports += 1
            
            # Progress indicator
            if (idx + 1) % 100 == 0:
                print(f"   Processed {idx + 1}/{len(df)} resumes...")
                
        except Exception as e:
            print(f"ERROR: Error processing row {idx+1}: {e}")
            failed_exports += 1
    
    # Summary
    print(f"\nSplit Summary:")
    print(f"   SUCCESS: Successfully exported: {successful_exports} resumes")
    print(f"   ERROR: Failed exports: {failed_exports}")
    print(f"   Output directory: {output_folder}")
    
    if successful_exports > 0:
        print(f"\nSUCCESS: Resume splitting completed successfully!")
        print(f"   Next step: Run 'python Scripts/translate_resumes.py'")
        return True
    else:
        print(f"\nERROR: No resumes were successfully exported")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Resume Splitting Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("Scripts"):
        print("ERROR: Please run this script from the project root directory")
        sys.exit(1)
    
    # Run the splitting process
    success = split_resumes(CSV_PATH, OUTPUT_FOLDER)
    
    if not success:
        print("\nTroubleshooting tips:")
        print("1. Ensure resumes.csv exists in the data/ directory")
        print("2. Check that the CSV file contains resume text")
        print("3. Verify the CSV encoding (should be UTF-8)")
        print("4. Make sure you have write permissions in the data/ directory")
        sys.exit(1)

if __name__ == "__main__":
    main()
