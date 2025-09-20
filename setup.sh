#!/bin/bash

# 🏆 AuDite - Ayurvedic Diet Management Software
# Smart India Hackathon 2024 - Setup Script

echo "🏆 AuDite - Ayurvedic Diet Management Software"
echo "Smart India Hackathon 2024 - Setup Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are installed"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_warning "Node.js is not installed. Frontend development will not be available."
else
    print_status "Node.js is installed"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_warning "Python 3 is not installed. Backend development will not be available."
else
    print_status "Python 3 is installed"
fi

echo ""
print_info "Setting up AuDite..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_info "Creating .env file..."
    cat > .env << EOF
# Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Firebase Configuration
FIREBASE_CRED_PATH=secrets/firebase-adminsdk.json
GOOGLE_CLOUD_PROJECT=ayurvedic-diet-app
FIREBASE_DATABASE_URL=

# ML Models
ML_MODELS_BUCKET=gs://ayur-ml-models
MODEL_CACHE_SIZE=256
PREDICTION_CACHE_TTL=900

# Cloud Tasks
CLOUD_TASKS_QUEUE=projects/ayurvedic-diet-app/locations/us-central1/queues/ayur-tasks

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Database
FIRESTORE_COLLECTION_PREFIX=ayur_diet

# Monitoring
SENTRY_DSN=
LOG_LEVEL=INFO
EOF
    print_status ".env file created"
else
    print_info ".env file already exists"
fi

# Create secrets directory
mkdir -p secrets
print_status "Created secrets directory"

echo ""
print_info "🚀 Starting AuDite with Docker Compose..."

# Start the backend with Docker Compose
docker-compose up --build -d

if [ $? -eq 0 ]; then
    print_status "Backend started successfully!"
    echo ""
    print_info "🌐 Services are now running:"
    echo "   • Backend API: http://localhost:8000"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • ReDoc: http://localhost:8000/redoc"
    echo "   • Health Check: http://localhost:8000/health"
    echo ""
    print_info "📚 Next Steps:"
    echo "   1. Set up Firebase credentials in secrets/firebase-adminsdk.json"
    echo "   2. Update GOOGLE_CLOUD_PROJECT in .env file"
    echo "   3. For frontend development: cd frontend && npm install && npm run dev"
    echo ""
    print_status "🎉 AuDite is ready for Smart India Hackathon 2024!"
else
    print_error "Failed to start AuDite. Please check the logs."
    exit 1
fi
