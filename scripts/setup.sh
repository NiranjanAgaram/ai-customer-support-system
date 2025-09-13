#!/bin/bash

# AI Customer Support System - Setup Script
echo "🚀 Setting up AI Customer Support System..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Setup backend
setup_backend() {
    print_info "Setting up backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_status "Backend setup completed"
    cd ..
}

# Setup frontend
setup_frontend() {
    print_info "Setting up frontend..."
    cd frontend
    npm install
    print_status "Frontend setup completed"
    cd ..
}

# Create startup scripts
create_startup_scripts() {
    cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
    chmod +x start_backend.sh
    
    cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm run dev
EOF
    chmod +x start_frontend.sh
    
    print_status "Startup scripts created"
}

# Main setup
main() {
    setup_backend
    setup_frontend
    create_startup_scripts
    
    echo ""
    print_status "Setup completed!"
    echo "Start backend: ./start_backend.sh"
    echo "Start frontend: ./start_frontend.sh"
    echo "Frontend: http://localhost:3000"
    echo "Backend: http://localhost:8000"
}

main