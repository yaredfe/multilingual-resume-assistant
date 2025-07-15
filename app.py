import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Scripts'))

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import json
import tempfile
from typing import List, Dict, Any
import shutil
import PyPDF2
import io

from vector_store import init_chroma, load_parsed_resume_text
from semantic_matching import build_job_description_text
from interview_question_generator import generate_interview_questions
from translate_resumes import detect_language, translate_text
from parse_resumes import parse_resume
from parser_helpers import extract_email, extract_phone, extract_education, extract_experience, extract_skills

app = FastAPI(title="Multilingual Resume Screener & Interview Assistant", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variables
client = None
collection = None
embedding_model = None

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global client, collection, embedding_model
    try:
        client, collection = init_chroma()
        from sentence_transformers import SentenceTransformer
        embedding_model = SentenceTransformer("models/sentence-transformers/all-MiniLM-L6-v2")
        print("✅ Application initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main landing page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Multilingual Resume Screener & Interview Assistant</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .hero-section {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 80px 0;
            }
            .role-card {
                border: none;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
                cursor: pointer;
            }
            .role-card:hover {
                transform: translateY(-5px);
            }
            
            /* New AI Brain Design */
            .hero-illustration {
                position: relative;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 400px;
            }
            
            .ai-brain {
                position: relative;
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 2rem;
            }
            
            .neural-network {
                position: relative;
                width: 200px;
                height: 120px;
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                grid-template-rows: repeat(2, 1fr);
                gap: 20px;
            }
            
            .node {
                width: 20px;
                height: 20px;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 50%;
                position: relative;
                animation: pulse 2s infinite;
            }
            
            .node:nth-child(1) { animation-delay: 0s; }
            .node:nth-child(2) { animation-delay: 0.3s; }
            .node:nth-child(3) { animation-delay: 0.6s; }
            .node:nth-child(4) { animation-delay: 0.9s; }
            .node:nth-child(5) { animation-delay: 1.2s; }
            .node:nth-child(6) { animation-delay: 1.5s; }
            
            .node::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 30px;
                height: 2px;
                background: rgba(255, 255, 255, 0.3);
                transform: translate(-50%, -50%);
            }
            
            .node::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 2px;
                height: 30px;
                background: rgba(255, 255, 255, 0.3);
                transform: translate(-50%, -50%);
            }
            
            @keyframes pulse {
                0%, 100% { 
                    transform: scale(1);
                    opacity: 0.8;
                }
                50% { 
                    transform: scale(1.2);
                    opacity: 1;
                }
            }
            
            .tech-stack {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .tech-badge {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 600;
                border: 1px solid rgba(255, 255, 255, 0.3);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }
            
            .tech-badge:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <!-- Hero Section -->
        <div class="hero-section">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col-lg-6">
                        <h1 class="display-4 fw-bold mb-4">
                            <i class="fas fa-globe-americas me-3"></i>
                            Multilingual Resume Screener
                        </h1>
                        <p class="lead mb-4">
                            AI-powered resume screening and interview question generation 
                            supporting English, French, German, and Spanish resumes.
                        </p>
                    </div>
                    <div class="col-lg-6 text-center">
                        <div class="hero-illustration">
                            <div class="ai-brain">
                                <i class="fas fa-brain" style="font-size: 4rem; color: #fff; margin-bottom: 1rem;"></i>
                                <div class="neural-network">
                                    <div class="node"></div>
                                    <div class="node"></div>
                                    <div class="node"></div>
                                    <div class="node"></div>
                                    <div class="node"></div>
                                    <div class="node"></div>
                                </div>
                            </div>
                            <div class="tech-stack">
                                <span class="tech-badge">AI</span>
                                <span class="tech-badge">NLP</span>
                                <span class="tech-badge">ML</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Role Selection Section -->
        <div class="container my-5">
            <div class="row justify-content-center">
                <div class="col-lg-8 text-center">
                    <h2 class="mb-5">Choose Your Role</h2>
                    <div class="row">
                        <div class="col-md-6 mb-4">
                            <div class="card role-card h-100" onclick="window.location.href='/recruiter'">
                                <div class="card-body text-center p-5">
                                    <i class="fas fa-user-tie fa-4x text-primary mb-4"></i>
                                    <h4 class="card-title">Recruiter</h4>
                                    <p class="card-text">
                                        Upload job descriptions, find matching candidates, 
                                        and generate interview questions for top matches.
                                    </p>
                                    <button class="btn btn-primary btn-lg">
                                        <i class="fas fa-search me-2"></i>Find Candidates
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-4">
                            <div class="card role-card h-100" onclick="window.location.href='/employee'">
                                <div class="card-body text-center p-5">
                                    <i class="fas fa-user fa-4x text-success mb-4"></i>
                                    <h4 class="card-title">Job Seeker</h4>
                                    <p class="card-text">
                                        Upload your resume and find matching job opportunities 
                                        across multiple languages.
                                    </p>
                                    <button class="btn btn-success btn-lg">
                                        <i class="fas fa-upload me-2"></i>Upload Resume
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/recruiter", response_class=HTMLResponse)
async def recruiter_dashboard():
    """Recruiter dashboard for job posting and candidate matching"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recruiter Dashboard - Multilingual Resume Screener</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .hero-section {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 0;
            }
            .result-card {
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .contact-info {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <i class="fas fa-globe-americas me-2"></i>Resume Screener
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/"><i class="fas fa-home me-1"></i>Home</a>
                    <a class="nav-link active" href="/recruiter"><i class="fas fa-user-tie me-1"></i>Recruiter</a>
                    <a class="nav-link" href="/employee"><i class="fas fa-user me-1"></i>Employee</a>
                </div>
            </div>
        </nav>

        <!-- Hero Section -->
        <div class="hero-section">
            <div class="container">
                <h1><i class="fas fa-user-tie me-3"></i>Recruiter Dashboard</h1>
                <p class="lead">Find the best candidates for your job openings</p>
            </div>
        </div>

        <!-- Job Description Form -->
        <div class="container my-5">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h4 class="mb-0"><i class="fas fa-search me-2"></i>Find Matching Candidates</h4>
                        </div>
                        <div class="card-body">
                            <form id="jobDescriptionForm">
                                <div class="mb-3">
                                    <label for="jobTitle" class="form-label">Job Title</label>
                                    <input type="text" class="form-control" id="jobTitle" name="jobTitle" required>
                                </div>
                                <div class="mb-3">
                                    <label for="jobDescription" class="form-label">Job Description</label>
                                    <textarea class="form-control" id="jobDescription" name="jobDescription" rows="5" required></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="requirements" class="form-label">Requirements (one per line)</label>
                                    <textarea class="form-control" id="requirements" name="requirements" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="skills" class="form-label">Required Skills (comma-separated)</label>
                                    <input type="text" class="form-control" id="skills" name="skills">
                                </div>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-search me-2"></i>Find Matching Candidates
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Results Section -->
        <div class="container my-5" id="results-section" style="display: none;">
            <div class="row">
                <div class="col-12">
                    <h3><i class="fas fa-users me-2"></i>Top Matching Candidates</h3>
                    <div id="results-container"></div>
                </div>
            </div>
        </div>

        <!-- Loading Modal -->
        <div class="modal fade" id="loadingModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-body text-center">
                        <div class="spinner-border text-primary mb-3" role="status"></div>
                        <h5>Finding Best Candidates...</h5>
                        <p>This may take a few moments.</p>
                        <div class="progress mt-3" style="height: 4px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.getElementById('jobDescriptionForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const jobData = {
                    title: formData.get('jobTitle'),
                    description: formData.get('jobDescription'),
                    requirements: formData.get('requirements').split('\\n').filter(req => req.trim()),
                    skills: formData.get('skills').split(',').map(skill => skill.trim()).filter(skill => skill)
                };

                // Show loading modal
                const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
                loadingModal.show();

                try {
                    // Add timeout to the fetch request (90 seconds for complete processing)
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 90000);
                    
                    // Update loading message to show progress
                    const loadingBody = document.querySelector('#loadingModal .modal-body');
                    const progressBar = document.querySelector('#loadingModal .progress-bar');
                    
                    loadingBody.innerHTML = `
                        <div class="spinner-border text-primary mb-3" role="status"></div>
                        <h5>Finding Best Candidates...</h5>
                        <p>Analyzing job requirements and matching candidates...</p>
                        <div class="progress mt-3" style="height: 4px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 25%"></div>
                        </div>
                    `;
                    
                    const response = await fetch('/api/match-candidates', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(jobData),
                        signal: controller.signal
                    });

                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    // Update loading message for final processing
                    loadingBody.innerHTML = `
                        <div class="spinner-border text-primary mb-3" role="status"></div>
                        <h5>Generating Interview Questions...</h5>
                        <p>Creating personalized questions for each candidate...</p>
                        <div class="progress mt-3" style="height: 4px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 75%"></div>
                        </div>
                    `;
                    
                    const results = await response.json();
                    
                    // Small delay to show the final loading state
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                    // Hide modal and display results
                    loadingModal.hide();
                    displayResults(results);
                    
                } catch (error) {
                    console.error('Error:', error);
                    loadingModal.hide(); // Hide modal on error too
                    if (error.name === 'AbortError') {
                        alert('Request timed out. Please try again with a simpler job description.');
                    } else {
                        alert('An error occurred while processing your request. Please try again.');
                    }
                }
            });

            function displayResults(results) {
                const container = document.getElementById('results-container');
                const resultsSection = document.getElementById('results-section');
                
                container.innerHTML = '';
                
                results.candidates.forEach((candidate, index) => {
                    const card = document.createElement('div');
                    card.className = 'card result-card';
                    card.innerHTML = `
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Candidate ${index + 1} (Score: ${(1 - candidate.score).toFixed(3)})</h5>
                            <span class="badge bg-primary">${candidate.language}</span>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <h6>Resume Snippet:</h6>
                                    <p class="text-muted">${candidate.resume_snippet.substring(0, 300)}...</p>
                                    
                                    <div class="contact-info">
                                        <h6><i class="fas fa-address-card me-2"></i>Contact Information:</h6>
                                        <p><strong>Email:</strong> ${candidate.contact_info.email || 'Not available'}</p>
                                        <p><strong>Phone:</strong> ${candidate.contact_info.phone || 'Not available'}</p>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h6>Interview Questions:</h6>
                                    <ul class="list-unstyled">
                                        ${candidate.interview_questions.split('\\n').map(q => 
                                            `<li><i class="fas fa-question-circle text-primary me-2"></i>${q}</li>`
                                        ).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    `;
                    container.appendChild(card);
                });
                
                resultsSection.style.display = 'block';
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/employee", response_class=HTMLResponse)
async def employee_dashboard():
    """Employee dashboard for resume upload and job matching"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job Seeker Dashboard - Multilingual Resume Screener</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .hero-section {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 40px 0;
            }
            .upload-area {
                border: 2px dashed #dee2e6;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                transition: border-color 0.3s ease;
            }
            .upload-area:hover {
                border-color: #28a745;
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-success">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <i class="fas fa-globe-americas me-2"></i>Resume Screener
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/"><i class="fas fa-home me-1"></i>Home</a>
                    <a class="nav-link" href="/recruiter"><i class="fas fa-user-tie me-1"></i>Recruiter</a>
                    <a class="nav-link active" href="/employee"><i class="fas fa-user me-1"></i>Employee</a>
                </div>
            </div>
        </nav>

        <!-- Hero Section -->
        <div class="hero-section">
            <div class="container">
                <h1><i class="fas fa-user me-3"></i>Job Seeker Dashboard</h1>
                <p class="lead">Upload your resume and find matching job opportunities</p>
            </div>
        </div>

        <!-- Resume Upload Section -->
        <div class="container my-5">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h4 class="mb-0"><i class="fas fa-file-upload me-2"></i>Upload Your Resume</h4>
                        </div>
                        <div class="card-body">
                            <form id="resumeUploadForm">
                                <div class="upload-area" id="uploadArea">
                                    <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                                    <h5>Drag & Drop Resume Here</h5>
                                    <p class="text-muted">Supports PDF, TXT, and DOC files</p>
                                    <input type="file" id="resumeFile" name="resume_file" accept=".pdf,.txt,.doc,.docx" style="display: none;">
                                    <button type="button" class="btn btn-outline-success" onclick="document.getElementById('resumeFile').click()">
                                        <i class="fas fa-folder-open me-2"></i>Choose File
                                    </button>
                                </div>
                                <div class="mt-3">
                                    <button type="submit" class="btn btn-success" id="uploadBtn" disabled>
                                        <i class="fas fa-upload me-2"></i>Upload Resume
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            const resumeFile = document.getElementById('resumeFile');
            const uploadBtn = document.getElementById('uploadBtn');
            const uploadArea = document.getElementById('uploadArea');

            // File selection handling
            resumeFile.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    uploadBtn.disabled = false;
                    uploadArea.innerHTML = `
                        <i class="fas fa-file fa-3x text-success mb-3"></i>
                        <h5>File Selected: ${e.target.files[0].name}</h5>
                        <p class="text-muted">Ready to upload</p>
                    `;
                }
            });

            // Drag and drop handling
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = '#28a745';
            });

            uploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = '#dee2e6';
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = '#dee2e6';
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    resumeFile.files = files;
                    uploadBtn.disabled = false;
                    uploadArea.innerHTML = `
                        <i class="fas fa-file fa-3x text-success mb-3"></i>
                        <h5>File Selected: ${files[0].name}</h5>
                        <p class="text-muted">Ready to upload</p>
                    `;
                }
            });

            // Resume upload form
            document.getElementById('resumeUploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData();
                formData.append('resume_file', resumeFile.files[0]);

                try {
                    const response = await fetch('/api/upload-resume', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    if (result.success) {
                        alert('Resume uploaded successfully!');
                        document.getElementById('resumeUploadForm').reset();
                        uploadBtn.disabled = true;
                        uploadArea.innerHTML = `
                            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                            <h5>Drag & Drop Resume Here</h5>
                            <p class="text-muted">Supports PDF, TXT, and DOC files</p>
                            <input type="file" id="resumeFile" name="resume_file" accept=".pdf,.txt,.doc,.docx" style="display: none;">
                            <button type="button" class="btn btn-outline-success" onclick="document.getElementById('resumeFile').click()">
                                <i class="fas fa-folder-open me-2"></i>Choose File
                            </button>
                        `;
                    } else {
                        alert('Error uploading resume: ' + result.error);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred while uploading the resume.');
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/match-candidates")
async def match_candidates(job_data: Dict[str, Any]):
    """Match job description with top 5 candidates and generate interview questions"""
    try:
        # Build job description text
        job_text = build_job_description_text(job_data)
        
        # Embed job description
        job_embedding = embedding_model.encode(job_text).tolist()
        
        # Query top 5 matches
        results = collection.query(
            query_embeddings=[job_embedding], 
            n_results=5
        )
        
        # Prepare candidates data first
        candidates_data = []
        for i in range(len(results["documents"][0])):
            resume_snippet = results["documents"][0][i]
            score = results["distances"][0][i]
            
            # Extract contact information from resume
            contact_info = {
                "email": extract_email(resume_snippet),
                "phone": extract_phone(resume_snippet)
            }
            
            candidates_data.append({
                "resume_snippet": resume_snippet,
                "score": score,
                "contact_info": contact_info
            })
        
        # Generate interview questions for all candidates in parallel
        import asyncio
        import concurrent.futures
        
        async def generate_questions_for_candidate(candidate_data):
            try:
                # Set a timeout for question generation (30 seconds)
                questions = await asyncio.wait_for(
                    asyncio.to_thread(generate_interview_questions, job_data["title"], candidate_data["resume_snippet"]),
                    timeout=30.0
                )
                return questions
            except asyncio.TimeoutError:
                return "Interview questions generation timed out. Please try again."
            except Exception as e:
                return f"Error generating questions: {str(e)}"
        
        # Generate questions for all candidates simultaneously
        question_tasks = [generate_questions_for_candidate(candidate) for candidate in candidates_data]
        questions_results = await asyncio.gather(*question_tasks, return_exceptions=True)
        
        # Combine results
        candidates = []
        for i, candidate_data in enumerate(candidates_data):
            questions = questions_results[i] if not isinstance(questions_results[i], Exception) else f"Error: {str(questions_results[i])}"
            
            # Detect language (simplified - assume English for now)
            language = "English"  # This could be enhanced with language detection
            
            candidates.append({
                "resume_snippet": candidate_data["resume_snippet"],
                "score": candidate_data["score"],
                "interview_questions": questions,
                "language": language,
                "contact_info": candidate_data["contact_info"]
            })
        
        return {
            "success": True,
            "candidates": candidates,
            "job_title": job_data["title"]
        }
        
    except Exception as e:
        print(f"Error in match_candidates: {e}")
        raise HTTPException(status_code=500, detail=f"Error matching candidates: {str(e)}")

@app.post("/api/upload-resume")
async def upload_resume(resume_file: UploadFile = File(...)):
    """Upload and process a new resume"""
    try:
        # Check file type
        if not resume_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = resume_file.filename.lower().split('.')[-1]
        
        # Extract text based on file type
        if file_extension == 'pdf':
            # Read PDF content
            content = await resume_file.read()
            pdf_file = io.BytesIO(content)
            text_content = extract_text_from_pdf(pdf_file)
        elif file_extension in ['txt', 'doc', 'docx']:
            # Read text content
            content = await resume_file.read()
            text_content = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, TXT, or DOC files.")
        
        # Detect language
        lang = detect_language(text_content)
        
        # Translate if not English
        if lang in ['fr', 'es', 'de']:
            translated_content = translate_text(text_content, lang)
            # Parse both original and translated
            original_parsed = parse_resume(text_content)
            translated_parsed = parse_resume(translated_content)
            
            # Use translated content for vector store
            final_content = translated_content
        else:
            # Parse English content
            original_parsed = parse_resume(text_content)
            final_content = text_content
        
        # Add to vector store
        collection.add(
            documents=[final_content],
            ids=[f"uploaded_{resume_file.filename}"]
        )
        
        return {
            "success": True,
            "message": f"Resume uploaded and processed successfully. Language detected: {lang}",
            "filename": resume_file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading resume: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Multilingual Resume Screener is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port) 