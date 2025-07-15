# Contributing to Multilingual Resume Assistant

Thank you for your interest in contributing to the Multilingual Resume Assistant! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs
- Use the GitHub issue tracker
- Include detailed steps to reproduce the bug
- Provide system information and error logs
- Check if the issue has already been reported

### Suggesting Enhancements
- Use the GitHub issue tracker with the "enhancement" label
- Describe the feature and its benefits
- Include mockups or examples if applicable

### Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Create a Pull Request

## 📋 Development Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Git

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/multilingual-resume-assistant.git
cd multilingual-resume-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start development server
uvicorn src.api.main:app --reload
```

### Docker Development
```bash
# Build development image
docker build -t multilingual-resume-assistant:dev .

# Run with volume mounting for development
docker run -p 8000:8000 -v $(pwd):/app multilingual-resume-assistant:dev
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/api/
```

### Writing Tests
- Follow the existing test structure
- Use descriptive test names
- Mock external dependencies
- Test both success and error cases
- Aim for high test coverage

## 📝 Code Style

### Python
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Keep functions small and focused
- Use meaningful variable names

### Example
```python
def process_resume(resume_text: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a resume and extract structured information.
    
    Args:
        resume_text: The raw resume text to process
        language: Optional language code for processing
        
    Returns:
        Dictionary containing extracted resume information
        
    Raises:
        ResumeProcessingError: If processing fails
    """
    # Implementation here
    pass
```

## 🔧 Configuration

### Environment Variables
- Use the `.env.example` file as a template
- Never commit sensitive information
- Document all new environment variables

### Adding New Features
1. Update configuration in `src/core/config.py`
2. Add validation in the Config class
3. Update documentation
4. Add tests for new configuration

## 📚 Documentation

### Code Documentation
- All public functions must have docstrings
- Use Google-style docstring format
- Include type hints
- Document exceptions and edge cases

### API Documentation
- Update OpenAPI specifications
- Include request/response examples
- Document error codes and messages

## 🚀 Deployment

### Production Checklist
- [ ] All tests pass
- [ ] Code coverage > 80%
- [ ] Documentation updated
- [ ] Environment variables documented
- [ ] Docker image builds successfully
- [ ] Performance tested

### Release Process
1. Update version in `src/__init__.py`
2. Update `CHANGELOG.md`
3. Create release tag
4. Deploy to production
5. Monitor for issues

## 🐛 Debugging

### Common Issues
1. **Model Loading Errors**: Check model file paths and permissions
2. **Memory Issues**: Reduce batch sizes or use smaller models
3. **Translation Failures**: Verify internet connection and model downloads
4. **Database Errors**: Check ChromaDB configuration and disk space

### Logging
- Use structured logging with appropriate levels
- Include context in log messages
- Don't log sensitive information

## 📞 Getting Help

- Create an issue for bugs or questions
- Join our discussions for general questions
- Check existing documentation first
- Be respectful and patient with maintainers

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Multilingual Resume Assistant! 🚀 