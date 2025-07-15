#!/bin/bash

# Multilingual Resume Screener Docker Deployment Script

echo "============================================================"
echo "Multilingual Resume Screener Docker Deployment"
echo "============================================================"

# Set image name and tag
IMAGE_NAME="multilingual-resume-screener"
TAG="latest"
CONTAINER_NAME="resume-screener-app"

# Function to stop and remove existing container
stop_container() {
    echo "Stopping existing container..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
}

# Function to start container
start_container() {
    echo "Starting container..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p 8000:8000 \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/models:/app/models \
        -v $(pwd)/static:/app/static \
        --restart unless-stopped \
        $IMAGE_NAME:$TAG
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if image exists
if ! docker image inspect $IMAGE_NAME:$TAG > /dev/null 2>&1; then
    echo "❌ Docker image not found. Please build the image first:"
    echo "   ./docker-build.sh"
    exit 1
fi

# Stop existing container
stop_container

# Start new container
start_container

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully!"
    echo ""
    echo "Application is running at:"
    echo "  http://localhost:8000"
    echo ""
    echo "To view logs:"
    echo "  docker logs -f $CONTAINER_NAME"
    echo ""
    echo "To stop the container:"
    echo "  docker stop $CONTAINER_NAME"
    echo ""
    echo "To restart:"
    echo "  docker restart $CONTAINER_NAME"
else
    echo "❌ Failed to start container!"
    exit 1
fi 