#!/bin/bash

# GIS Energy Optimizer Deployment Script
# Author: Hoang Tuan Dat
# Description: Deploy streamlit-geospatial application using Docker Compose

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed!"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data/logs
    mkdir -p data/cache
    mkdir -p data/uploads
    
    print_success "Directories created!"
}

# Function to check environment variables
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Copying from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before deploying."
        read -p "Press Enter to continue after editing .env file..."
    fi
    
    print_success "Environment configuration checked!"
}

# Function to check network connectivity to Langflow
check_langflow_connectivity() {
    print_status "Checking Langflow connectivity..."
    
    # Extract Langflow URL from .env file
    LANGFLOW_URL=$(grep LANGFLOW_API_URL .env | cut -d '=' -f2 | tr -d '"')
    
    if [ -z "$LANGFLOW_URL" ]; then
        print_warning "LANGFLOW_API_URL not set in .env file"
        return
    fi
    
    # Convert host.docker.internal to localhost for testing
    TEST_URL=$(echo "$LANGFLOW_URL" | sed 's/host\.docker\.internal/localhost/')
    
    if curl -s --max-time 5 "$TEST_URL" > /dev/null 2>&1; then
        print_success "Langflow is accessible!"
    else
        print_warning "Cannot reach Langflow at $TEST_URL"
        print_warning "Make sure Langflow is running before using the AI features"
    fi
}

# Function to build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Build the application
    print_status "Building streamlit-geospatial image..."
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    print_success "Services started!"
}

# Function to show service status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo ""
    print_status "Service logs (last 10 lines):"
    docker-compose logs --tail=10
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for Streamlit app
    for i in {1..30}; do
        if curl -s http://localhost:8502/_stcore/health > /dev/null 2>&1; then
            print_success "Streamlit app is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Timeout waiting for Streamlit app"
            exit 1
        fi
        sleep 2
    done
    
    # Wait for Nginx proxy
    for i in {1..30}; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            print_success "Nginx proxy is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "Nginx proxy might not be ready"
        fi
        sleep 2
    done
}

# Function to show access information
show_access_info() {
    echo ""
    print_success "🎉 Deployment completed successfully!"
    echo ""
    echo -e "${GREEN}Access Information:${NC}"
    echo -e "  📱 Direct Streamlit App: ${BLUE}http://localhost:8502${NC}"
    echo -e "  🌐 Nginx Proxy:         ${BLUE}http://localhost:8080${NC}"
    echo -e "  💾 Redis Cache:         ${BLUE}http://localhost:6381${NC}"
    echo ""
    echo -e "${GREEN}Useful Commands:${NC}"
    echo -e "  📊 View logs:           ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  🔄 Restart services:    ${YELLOW}docker-compose restart${NC}"
    echo -e "  🛑 Stop services:       ${YELLOW}docker-compose down${NC}"
    echo -e "  🔍 Check status:        ${YELLOW}docker-compose ps${NC}"
    echo ""
    echo -e "${GREEN}Features Available:${NC}"
    echo -e "  🌍 Interactive GIS mapping with Vietnam energy infrastructure"
    echo -e "  🤖 AI-powered chatbot integration with Langflow"
    echo -e "  📊 Real-time energy consumption visualization"
    echo -e "  🗺️ Advanced geospatial analysis tools"
    echo -e "  📈 Heat maps and efficiency analytics"
    echo ""
}

# Function to cleanup on exit
cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Deployment failed. Cleaning up..."
        docker-compose down 2>/dev/null || true
    fi
}

# Main deployment function
main() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "   GIS Energy Optimizer Deployment Script"
    echo "=================================================="
    echo -e "${NC}"
    
    trap cleanup EXIT
    
    check_prerequisites
    create_directories
    check_environment
    check_langflow_connectivity
    deploy_services
    wait_for_services
    show_status
    show_access_info
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose down
        print_success "Services stopped!"
        ;;
    "restart")
        print_status "Restarting services..."
        docker-compose restart
        print_success "Services restarted!"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        show_status
        ;;
    "clean")
        print_status "Cleaning up..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_success "Cleanup completed!"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|clean}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the application (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        echo "  status   - Show service status"
        echo "  clean    - Stop services and clean up resources"
        exit 1
        ;;
esac