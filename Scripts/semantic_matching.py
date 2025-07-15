import os
import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHROMA_DB_DIR = "data/chroma_db"
JOB_DESCRIPTION_FOLDER = "data/job_descriptions"
MATCH_RESULT_FOLDER = "data/match_results"
TOP_K = 5

def build_job_description_text(data):
    """Build a comprehensive job description text from structured data"""
    parts = []
    
    if "title" in data and data["title"]:
        parts.append(f"Job Title: {data['title']}")
    
    if "description" in data and data["description"]:
        parts.append(f"Description: {data['description']}")
    
    if "requirements" in data and isinstance(data["requirements"], list) and data["requirements"]:
        requirements_text = "\n".join(f"- {req}" for req in data["requirements"])
        parts.append(f"Requirements:\n{requirements_text}")
    
    if "skills" in data and isinstance(data["skills"], list) and data["skills"]:
        skills_text = ", ".join(data["skills"])
        parts.append(f"Skills: {skills_text}")
    
    return "\n\n".join(parts).strip()

def get_top_matches(job_text, top_k=TOP_K):
    """Get top matching candidates for a job description"""
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        collection = client.get_collection(name="resume_collection")
        
        # Use the same embedding model as the collection
        embedder = SentenceTransformer("models/sentence-transformers/all-MiniLM-L6-v2")
        
        # Embed job description
        job_embedding = embedder.encode(job_text).tolist()
        
        # Query resumes by embedding vector
        results = collection.query(
            query_embeddings=[job_embedding], 
            n_results=top_k
        )
        
        return results
        
    except Exception as e:
        print(f"ERROR: Error in semantic matching: {e}")
        return None

def main():
    """Main function to process job descriptions and find matches"""
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        collection = client.get_collection(name="resume_collection")
        
        embedder = SentenceTransformer("models/sentence-transformers/all-MiniLM-L6-v2")
        
        # Ensure result folder exists
        os.makedirs(MATCH_RESULT_FOLDER, exist_ok=True)
        
        processed_count = 0
        error_count = 0
        
        for filename in os.listdir(JOB_DESCRIPTION_FOLDER):
            if not filename.endswith(".json"):
                continue
                
            filepath = os.path.join(JOB_DESCRIPTION_FOLDER, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    job_data = json.load(f)
            except Exception as e:
                print(f"ERROR: Failed to load {filename}: {e}")
                error_count += 1
                continue

            job_text = build_job_description_text(job_data)
            if not job_text:
                print(f"ERROR: Could not parse {filename}, skipping.")
                error_count += 1
                continue

            # Get matches
            results = get_top_matches(job_text)
            if not results:
                print(f"ERROR: No matches found for {filename}")
                error_count += 1
                continue

            print(f"\n📋 Top {TOP_K} matches for '{job_data.get('title', filename)}':\n")
            for i in range(len(results["documents"][0])):
                print(f"Rank {i+1}")
                print(f"Resume Snippet: {results['documents'][0][i][:300]}...")
                print(f"Score: {results['distances'][0][i]:.4f}")
                if results['metadatas'] and results['metadatas'][0]:
                    print(f"Metadata: {results['metadatas'][0][i]}")
                print("-" * 40)

            # Save to result file
            job_title = job_data.get("title", os.path.splitext(filename)[0])
            safe_title = "".join(c for c in job_title if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
            result_path = os.path.join(MATCH_RESULT_FOLDER, f"{safe_title}.json")

            match_results = []
            for i in range(len(results["documents"][0])):
                match_result = {
                    "rank": i + 1,
                    "resume_snippet": results["documents"][0][i],
                    "score": results["distances"][0][i]
                }
                
                # Add metadata if available
                if results['metadatas'] and results['metadatas'][0]:
                    match_result["metadata"] = results['metadatas'][0][i]
                
                match_results.append(match_result)

            with open(result_path, "w", encoding="utf-8") as out_file:
                json.dump(match_results, out_file, indent=2, ensure_ascii=False)
            
            processed_count += 1
            print(f"💾 Saved results to: {result_path}")

        print(f"\n Summary: Processed {processed_count} job descriptions, {error_count} errors")

    except Exception as e:
        print(f"ERROR: Error in main processing: {e}")

if __name__ == "__main__":
    main()
