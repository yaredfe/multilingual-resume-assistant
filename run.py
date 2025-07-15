#!/usr/bin/env python3
"""
Multilingual Resume Screener & Interview Assistant
Startup script for the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import chromadb
        import transformers
        import sentence_transformers
        import spacy
        print("SUCCESS: All required packages are installed")
        return True
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_models():
    """Check if required models are available"""
    print("Checking models...")
    
    model_paths = [
        "models/sentence-transformers/all-MiniLM-L6-v2",
        "models/flan-t5-base",
        "models/opus-mt-fr-en",
        "models/opus-mt-es-en", 
        "models/opus-mt-de-en"
    ]
    
    missing_models = []
    for path in model_paths:
        if not os.path.exists(path):
            missing_models.append(path)
    
    if missing_models:
        print("ERROR: Missing models:")
        for model in missing_models:
            print(f"   - {model}")
        print("\nPlease download the required models first.")
        return False
    
    print("SUCCESS: All required models are available")
    return True

def check_data():
    """Check if data directories exist"""
    print("Checking data directories...")
    
    data_dirs = [
        "data/resumes",
        "data/parsed",
        "data/chroma_db"
    ]
    
    missing_dirs = []
    for dir_path in data_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("WARNING: Missing data directories:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        print("\nPlease run the data setup scripts first:")
        print("   python Scripts/split_resumes.py")
        print("   python Scripts/translate_resumes.py")
        print("   python Scripts/parse_resumes.py")
        print("   python Scripts/vector_store.py")
        return False
    
    print("SUCCESS: Data directories are ready")
    return True

def setup_environment():
    """Setup environment variables"""
    print("Setting up environment...")
    
    # Set default environment variables
    os.environ.setdefault("CHROMA_DB_PATH", "data/chroma_db")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8000")
    
    print("SUCCESS: Environment configured")

def run_app():
    """Run the FastAPI application"""
    print("Starting Multilingual Resume Screener...")
    
    try:
        import uvicorn
        
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        
        print(f"Server will be available at: http://{host}:{port}")
        print("API documentation will be available at: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        
        # Use subprocess to run uvicorn with proper error handling
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", host, 
            "--port", str(port),
            "--reload"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"ERROR: Error starting server: {e}")
        print("Trying alternative method...")
        try:
            # Alternative: direct uvicorn call
            os.system(f"uvicorn app:app --host {host} --port {port} --reload")
        except Exception as e2:
            print(f"ERROR: Alternative method also failed: {e2}")
            sys.exit(1)

def main():
    """Main function"""
    print("=" * 60)
    print("Multilingual Resume Screener & Interview Assistant")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("ERROR: Please run this script from the project root directory")
        sys.exit(1)
    
    # Run checks
    if not check_dependencies():
        sys.exit(1)
    
    if not check_models():
        print("\nTo download models, run:")
        print("   python -m spacy download en_core_web_sm")
        print("   # Download other models as needed")
        sys.exit(1)
    
    if not check_data():
        print("\nTo setup data, run the setup scripts or start with empty data")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    setup_environment()
    
    # Start the application
    run_app()

if __name__ == "__main__":
    main() 