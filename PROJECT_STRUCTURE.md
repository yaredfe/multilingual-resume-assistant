# Multilingual Resume Assistant - Project Structure

## Overview
This is a production-ready multilingual resume screening and interview assistant application built with FastAPI, Docker, and AI/ML technologies.

## Project Structure

```
multilingual-resume-assistant/
├── 📁 Core Application
│   ├── app.py                    # Main FastAPI application
│   ├── config.py                 # Configuration management
│   ├── run.py                    # Application entry point
│   └── env.example               # Environment variables template
│
├── 📁 Production-Ready Architecture (src/)
│   ├── api/                      # API layer
│   │   └── main.py              # API endpoints and routing
│   ├── services/                 # Business logic layer
│   │   ├── semantic_matching.py # Job-candidate matching service
│   │   ├── resume_parser.py     # Resume parsing service
│   │   └── translation.py       # Translation service
│   └── core/                     # Core utilities
│       ├── config.py            # Configuration management
│       ├── exceptions.py        # Custom exception handling
│       └── __init__.py          # Core module initialization
│
├── 📁 Scripts (Legacy - for data processing)
│   ├── parse_resumes.py         # Resume parsing utilities
│   ├── interview_question_generator.py # AI question generation
│   ├── translate_resumes.py     # Translation utilities
│   └── ...                      # Other processing scripts
│
├── 📁 Data & Models
│   ├── data/                    # Application data
│   │   ├── resumes/            # Resume files
│   │   ├── parsed/             # Parsed resume data
│   │   ├── job_descriptions/   # Job description files
│   │   ├── interview_questions/ # Generated questions
│   │   └── chroma_db/          # Vector database
│   ├── models/                  # AI/ML models
│   │   ├── flan-t5-base/       # Interview question generator
│   │   ├── sentence-transformers/ # Semantic matching
│   │   └── opus-mt-*/          # Translation models
│   └── static/                  # Frontend assets
│
├── 📁 Docker & Deployment
│   ├── Dockerfile               # Main production Dockerfile
│   ├── Dockerfile-simple        # Simplified Dockerfile (learning)
│   ├── Dockerfile-alternative   # Alternative approach (learning)
│   ├── docker-compose.yml       # Multi-container setup
│   ├── docker-build.sh          # Build automation script
│   ├── docker-deploy.sh         # Deployment automation script
│   ├── DOCKER_README.md         # Docker documentation
│   ├── .dockerignore            # Docker build exclusions
│   └── requirements-docker.txt  # Docker-specific dependencies
│
├── 📁 Documentation
│   ├── README.md                # Project overview and setup
│   ├── CHANGELOG.md             # Version history
│   ├── CONTRIBUTING.md          # Contribution guidelines
│   ├── LICENSE                  # MIT License
│   └── PROJECT_STRUCTURE.md     # This file
│
└── 📁 Development
    ├── requirements.txt         # Development dependencies
    ├── .gitignore              # Git exclusions
    └── venv/                   # Virtual environment (local)
```

## Key Features

### 🏗️ **Architecture**
- **Clean Architecture**: Separation of concerns with API, Services, and Core layers
- **Production-Ready**: Proper error handling, logging, and configuration management
- **Scalable**: Modular design allowing easy extension and maintenance

### 🐳 **Docker Expertise**
- **Multiple Dockerfiles**: Demonstrates different approaches and best practices
- **Docker Compose**: Multi-container orchestration
- **Build Automation**: Scripts for streamlined deployment
- **Documentation**: Comprehensive Docker guides and examples

### 🤖 **AI/ML Integration**
- **Semantic Matching**: Advanced job-candidate matching using embeddings
- **Interview Generation**: AI-powered question generation for specific roles
- **Multilingual Support**: Translation capabilities for global recruitment
- **Resume Parsing**: Intelligent extraction of candidate information

### 🌐 **Web Application**
- **FastAPI Backend**: Modern, fast, and auto-documented API
- **Responsive Frontend**: Bootstrap-based UI with modern design
- **Real-time Processing**: Asynchronous job matching and question generation

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for semantic search
- **spaCy**: NLP for resume parsing
- **Transformers**: Hugging Face models for AI tasks

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **JavaScript**: Interactive client-side functionality
- **HTML/CSS**: Clean, modern interface

### DevOps
- **Docker**: Containerization and deployment
- **Docker Compose**: Multi-service orchestration
- **Shell Scripts**: Automation and deployment

### AI/ML
- **Sentence Transformers**: Semantic embeddings
- **T5 Models**: Text generation for interview questions
- **Translation Models**: Multilingual support

## Learning Value

This project demonstrates:
- **Production Software Development**: Real-world application with proper architecture
- **Docker Mastery**: Multiple approaches and best practices
- **AI/ML Integration**: Practical implementation of modern AI technologies
- **Full-Stack Development**: Complete web application from backend to frontend
- **DevOps Practices**: Deployment automation and containerization
- **Code Organization**: Clean, maintainable, and scalable code structure

## Getting Started

1. **Clone the repository**
2. **Read the README.md** for setup instructions
3. **Explore the Docker files** to understand different approaches
4. **Run the application** using Docker Compose
5. **Test the features** through the web interface

This project showcases professional software development skills with modern technologies and best practices. 