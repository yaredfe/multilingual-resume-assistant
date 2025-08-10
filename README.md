
# 🌍 Multilingual Resume Assistant

> **AI-Powered Resume Analysis and Job Matching System**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A sophisticated, production-ready system for parsing, analyzing, and matching resumes with job descriptions using advanced Natural Language Processing (NLP) and Machine Learning techniques. Built with scalability, multilingual support, and enterprise-grade architecture in mind.

## Version

Initial Release (v1.0.0)

## 🚀 Features

### ✨ Core Capabilities
- **🔍 Intelligent Resume Parsing**: Extract structured information from resumes in multiple formats (PDF, TXT, DOCX)
- **🌐 Multilingual Support**: Detect and translate resumes from Spanish, French, German to English
- **🎯 Semantic Job Matching**: Advanced AI-powered matching between resumes and job descriptions
- **📊 Skills Analysis**: Comprehensive skills extraction and competency assessment
- **🤖 Interview Question Generation**: AI-generated relevant interview questions based on resume content
- **📈 Confidence Scoring**: Reliable confidence metrics for all extracted information

### 🏗️ Technical Excellence
- **Microservices Architecture**: Modular, scalable design with clear separation of concerns
- **Production-Ready API**: RESTful API with comprehensive error handling and validation
- **Docker Containerization**: Easy deployment and scaling with Docker
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Configuration Management**: Environment-based configuration with validation
- **Custom Exception Handling**: Robust error handling with meaningful error messages

## 🛠️ Technology Stack

### Backend & AI
- **Python 3.11+**: Modern Python with type hints and dataclasses
- **FastAPI**: High-performance web framework for building APIs
- **spaCy**: Industrial-strength Natural Language Processing
- **Transformers (Hugging Face)**: State-of-the-art machine learning models
- **Sentence Transformers**: Semantic text embeddings for matching
- **ChromaDB**: Vector database for similarity search

### Translation & Language Processing
- **MarianMT Models**: Pre-trained translation models for multiple languages
- **langdetect**: Language detection with high accuracy
- **dateparser**: Intelligent date parsing and extraction

### Infrastructure & Deployment
- **Docker**: Containerization for consistent deployment
- **Docker Compose**: Multi-container orchestration
- **Uvicorn**: ASGI server for production deployment
- **PostgreSQL**: Robust database for data persistence (configurable)

## 📁 Project Structure

```
multilingual-resume-assistant/
├── src/                          # Main source code
│   ├── core/                     # Core functionality
│   │   ├── config.py            # Configuration management
│   │   └── exceptions.py        # Custom exceptions
│   ├── services/                 # Business logic services
│   │   ├── translation.py       # Language detection & translation
│   │   ├── resume_parser.py     # Resume parsing & extraction
│   │   ├── semantic_matching.py # Job-resume matching
│   │   └── interview_generator.py # Interview question generation
│   ├── api/                      # API layer
│   │   ├── routes/              # API endpoints
│   │   ├── middleware/          # Custom middleware
│   │   └── models/              # Pydantic models
│   └── utils/                    # Utility functions
├── data/                         # Data storage
│   ├── resumes/                 # Raw resume files
│   ├── parsed/                  # Parsed resume data
│   ├── job_descriptions/        # Job description files
│   └── models/                  # ML model storage
├── tests/                        # Comprehensive test suite
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
├── docker/                       # Docker configuration
└── config/                       # Configuration files
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Docker and Docker Compose
- 8GB+ RAM (for ML models)
- 10GB+ disk space

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/multilingual-resume-assistant.git
cd multilingual-resume-assistant

# Build and run with Docker
docker build -t multilingual-resume-assistant:latest .
docker run -p 8000:8000 multilingual-resume-assistant:latest
```

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/multilingual-resume-assistant.git
cd multilingual-resume-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download required models
python scripts/setup_models.py

# Run the application
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Documentation

Once the application is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

### Key Endpoints

#### Resume Processing
```http
POST /api/resume/upload
POST /api/resume/parse
GET /api/resume/{resume_id}
```

#### Job Matching
```http
POST /api/match/resume-job
GET /api/match/similar-jobs/{resume_id}
```

#### Interview Questions
```http
POST /api/interview/generate-questions
GET /api/interview/questions/{resume_id}
```

## 🛠️ Configuration

The application uses environment variables for configuration:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Model Configuration
MODEL_DIR=models
SPACY_MODEL=en_core_web_sm
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2

# Processing Configuration
MAX_FILE_SIZE=10485760  # 10MB
CONFIDENCE_THRESHOLD=0.7
```

## 📈 Performance & Scalability

### Benchmarks
- **Resume Parsing**: ~2-5 seconds per resume (performance may vary depending on hardware and data size)
- **Language Detection**: ~0.1 seconds
- **Translation**: ~1-3 seconds (depending on text length)
- **Job Matching**: ~0.5-2 seconds per job description
- **Concurrent Requests**: 100+ requests per minute

### Scalability Features
- **Model Caching**: Pre-loaded models for faster inference
- **Batch Processing**: Efficient batch operations for multiple resumes
- **Async Processing**: Non-blocking operations for better performance
- **Resource Management**: Memory-efficient model loading and cleanup

## 🔒 Security & Privacy

- **Input Validation**: Comprehensive validation of all inputs
- **File Upload Security**: Secure file handling with size and type restrictions
- **Data Privacy**: No data persistence without explicit consent
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Error Handling**: Secure error messages without information leakage

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/multilingual-resume-assistant.git

# Create feature branch (replace amazing-feature with your feature name)
git checkout -b feature/your-feature-name

# Make your changes and add tests (if any)
# Commit your changes
git commit -m 'Add amazing feature'

# Push to branch
git push origin feature/your-feature-name

# Create Pull Request
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugging Face**: For the excellent transformer models
- **spaCy**: For industrial-strength NLP capabilities
- **FastAPI**: For the modern, fast web framework
- **OpenAI**: For inspiration in AI-powered applications

## 📞 Support & Contact

- **Author**: Yared Fereja
- **Email**: yaredfereja864@gmail.com
- **LinkedIn**: [Yared Fereja](https://www.linkedin.com/in/yared-fereja-067872326/)
- **GitHub**: [@yaredfe](https://github.com/yaredfe)

## 🗺️ Roadmap

### Version 2.0 (Q2 2024)
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Integration with popular ATS systems
- [ ] Mobile application
- [ ] Advanced ML model fine-tuning

### Version 1.5 (Q1 2024)
- [ ] Additional language support (Italian, Portuguese, Dutch)
- [ ] Enhanced skill extraction with confidence scoring
- [ ] Resume scoring and ranking system
- [ ] Bulk processing capabilities
- [ ] Advanced filtering and search

### Version 1.0 (Current, Initial Release)
- [x] Core resume parsing functionality
- [x] Multilingual support (ES, FR, DE)
- [x] Semantic job matching
- [x] Interview question generation
- [x] Production-ready API
- [x] Docker deployment

---

**⭐ Star this repository if you find it useful!**

*Built with ❤️ and ☕ by Yared Fereja*

## ⚠️ Known Issues

- The interview question generation feature is currently under development and not functional. I am actively working to resolve this. All other features are available for use and testing.
