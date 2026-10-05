@echo off
REM CloudDesk AI Support System - Setup Script for Windows

echo ================================
echo CloudDesk AI Support System
echo Automated Setup Script - Windows
echo ================================
echo.

REM Check Python version
echo Checking Python version...
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements-full.txt

REM Initialize database
echo Initializing database...
python << 'PYTHON_SCRIPT'
from database import DatabaseManager
db = DatabaseManager()
print("Database initialized successfully")
PYTHON_SCRIPT

REM Create .env template
echo Creating .env configuration...
(
echo # RAG Configuration
echo HF_TOKEN=your_huggingface_token
echo HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1
echo PINECONE_API_KEY=your_pinecone_key
echo PINECONE_INDEX_NAME=clouddesk
echo.
echo # Cache Configuration
echo CACHE_TTL_SECONDS=86400
echo CACHE_ENABLED=True
echo.
echo # Escalation Configuration
echo ESCALATION_CONFIDENCE_THRESHOLD=0.6
echo AUTO_ESCALATION_ENABLED=True
echo.
echo # Learning Configuration
echo LEARNING_ENABLED=True
echo LEARNING_CONFIDENCE_THRESHOLD=0.7
echo.
echo # API Configuration
echo API_HOST=0.0.0.0
echo API_PORT=5000
echo API_DEBUG=False
) > .env.example

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Configure your API keys in .env:
echo    - Copy .env.example to .env
echo    - Edit .env with your credentials
echo.
echo 2. Run the main application:
echo    streamlit run streamlit_app.py
echo.
echo 3. Access dashboards:
echo    Admin:     streamlit run dashboards/admin_dashboard.py
echo    Analytics: streamlit run dashboards/analytics_dashboard.py
echo.
echo 4. Start API server:
echo    python -m flask --app api.routes run
echo.
echo Documentation: See SYSTEM_DOCUMENTATION.md
echo Ready to launch CloudDesk!
pause
