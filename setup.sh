#!/bin/bash

# Airflow Docker Setup Script
# This script helps you set up Apache Airflow with Docker quickly

set -e

echo "🚀 Setting up Apache Airflow with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Set AIRFLOW_UID for Linux/macOS
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        echo "AIRFLOW_UID=$(id -u)" >> .env
        echo "✅ Set AIRFLOW_UID to $(id -u)"
    fi
else
    echo "✅ .env file already exists"
fi

# Check system requirements
echo "🔍 Checking system requirements..."

# Check available memory (Linux only)
if command -v free &> /dev/null; then
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$MEMORY_GB" -lt 4 ]; then
        echo "⚠️  Warning: You have ${MEMORY_GB}GB of RAM. At least 4GB is recommended."
    else
        echo "✅ Memory check passed (${MEMORY_GB}GB available)"
    fi
fi

# Initialize Airflow
echo "🔧 Initializing Airflow..."
docker compose up airflow-init

# Start services
echo "🚀 Starting Airflow services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if webserver is accessible
if curl -f http://localhost:8080/health &> /dev/null; then
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📊 Airflow is now running:"
    echo "   Web UI: http://localhost:8080"
    echo "   Username: airflow"
    echo "   Password: airflow"
    echo ""
    echo "🔧 Useful commands:"
    echo "   Stop services:    docker compose down"
    echo "   View logs:        docker compose logs -f"
    echo "   Restart services: docker compose restart"
    echo ""
else
    echo "⚠️  Setup completed, but webserver may still be starting."
    echo "   Please wait a few more minutes and try accessing http://localhost:8080"
fi