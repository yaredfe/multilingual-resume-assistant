#!/bin/bash

# Multilingual Resume Screener Docker Build Script

echo "============================================================"
echo "Building Multilingual Resume Screener Docker Image"
echo "============================================================"

# Set image name and tag
IMAGE_NAME="multilingual-resume-screener"
TAG="latest"

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "To run the container:"
    echo "  docker run -p 8000:8000 -v \$(pwd)/data:/app/data $IMAGE_NAME:$TAG"
    echo ""
    echo "Or use docker-compose:"
    echo "  docker-compose up -d"
    echo ""
    echo "To access the application:"
    echo "  http://localhost:8000"
else
    echo "❌ Docker build failed!"
    exit 1
fi 