#!/bin/bash
# CloudDesk AI Support System - Setup Script

echo "================================"
echo "CloudDesk AI Support System"
echo "Automated Setup Script"
echo "================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version

# Create virtual environment
echo "✓ Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-full.txt

# Initialize database
echo "✓ Initializing database..."
python3 << 'PYTHON_SCRIPT'
from database import DatabaseManager
db = DatabaseManager()
print("✓ Database initialized successfully")
PYTHON_SCRIPT

# Create .env template
echo "✓ Creating .env configuration..."
cat > .env.example << 'EOF'
# RAG Configuration
HF_TOKEN=your_huggingface_token
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=clouddesk

# Cache Configuration
CACHE_TTL_SECONDS=86400
CACHE_ENABLED=True

# Escalation Configuration
ESCALATION_CONFIDENCE_THRESHOLD=0.6
AUTO_ESCALATION_ENABLED=True

# Learning Configuration
LEARNING_ENABLED=True
LEARNING_CONFIDENCE_THRESHOLD=0.7

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=False

# Database
DATABASE_URL=clouddesk.db
EOF

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Configure your API keys in .env:"
echo "   cp .env.example .env"
echo "   # Edit .env with your credentials"
echo ""
echo "2. Run the main application:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "3. Access dashboards:"
echo "   Admin:     streamlit run dashboards/admin_dashboard.py"
echo "   Analytics: streamlit run dashboards/analytics_dashboard.py"
echo ""
echo "4. Start API server:"
echo "   python -m flask --app api.routes run"
echo ""
echo "📚 Documentation: See SYSTEM_DOCUMENTATION.md"
echo "🚀 Ready to launch CloudDesk!"
