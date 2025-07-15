import os
import json
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sentence_transformers import SentenceTransformer

MODEL_PATH = "models/sentence-transformers/all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_PATH)
embedding_function = SentenceTransformerEmbeddingFunction(model_name=MODEL_PATH)

def init_chroma():
    """Initialize ChromaDB client and collection"""
    try:
        # Use PersistentClient for local storage
        client = chromadb.PersistentClient(path="data/chroma_db")
        collection = client.get_or_create_collection(
            name="resume_collection",
            embedding_function=embedding_function
        )
        print("SUCCESS: ChromaDB initialized successfully")
        return client, collection
    except Exception as e:
        print(f"ERROR: Error initializing ChromaDB: {e}")
        raise

def load_parsed_resume_text(file_path):
    """Load and format parsed resume text for vector storage"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # If text field exists, use it directly
        if "text" in data:
            return data["text"].strip()

        # Build text from parsed components
        text_parts = []

        if "name" in data and data["name"]:
            text_parts.append(f"Name: {data['name']}")
        if "email" in data and data["email"]:
            text_parts.append(f"Email: {data['email']}")
        if "phone" in data and data["phone"]:
            text_parts.append(f"Phone: {data['phone']}")
        if "skills" in data and data["skills"]:
            text_parts.append("Skills: " + ", ".join(data["skills"]))
        if "education" in data and data["education"]:
            for edu in data["education"]:
                degree = edu.get("degree", "")
                institution = edu.get("institution", "")
                year = edu.get("year", "")
                text_parts.append(f"Education: {degree} from {institution}, Year: {year}")
        if "experience" in data and data["experience"]:
            for exp in data["experience"]:
                text_parts.append(f"Experience: {exp}")
        if "languages" in data and data["languages"]:
            text_parts.append("Languages: " + ", ".join(data["languages"]))

        return "\n".join(text_parts).strip()

    except Exception as e:
        print(f"ERROR: Error reading {file_path}: {e}")
        return None

def add_resume_to_store(resume_text, resume_id, metadata=None):
    """Add a single resume to the vector store"""
    try:
        client, collection = init_chroma()
        collection.add(
            documents=[resume_text],
            ids=[resume_id],
            metadatas=[metadata] if metadata else None
        )
        print(f"SUCCESS: Added resume {resume_id} to vector store")
        return True
    except Exception as e:
        print(f"ERROR: Error adding resume {resume_id}: {e}")
        return False

def main():
    """Main function to populate vector store with parsed resumes"""
    parsed_dir = "data/parsed"
    if not os.path.exists(parsed_dir):
        print(f"ERROR: Parsed directory not found: {parsed_dir}")
        return

    client, collection = init_chroma()
    added_count = 0
    error_count = 0

    for filename in os.listdir(parsed_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(parsed_dir, filename)
            resume_text = load_parsed_resume_text(file_path)

            if resume_text:
                try:
                    # Create metadata
                    metadata = {
                        "filename": filename,
                        "source": "parsed",
                        "language": "en"  # Default, could be enhanced with language detection
                    }
                    
                    collection.add(
                        documents=[resume_text],
                        ids=[filename],
                        metadatas=[metadata]
                    )
                    added_count += 1
                    print(f"SUCCESS: Added {filename} to vector store")
                except Exception as e:
                    error_count += 1
                    print(f"ERROR: Error adding {filename}: {e}")
            else:
                error_count += 1
                print(f"ERROR: No text found in {file_path}")

    print(f"\n Summary: Added {added_count} resumes, {error_count} errors")

if __name__ == "__main__":
    main()
