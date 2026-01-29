# 🏥 Healthcare Chatbot with RAG

AI-powered healthcare chatbot with RAG (Retrieval Augmented Generation), user authentication, health profile management, and PDF document analysis.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-success)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Windows Installation](#-windows-installation)
- [macOS/Linux Installation](#-macoslinux-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Docker Deployment](#-docker-deployment)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)

---

## ✨ Features

- ✅ **User Authentication** - Secure JWT-based authentication with bcrypt password hashing
- ✅ **Health Profile Management** - Comprehensive health information forms:
  - Basic information (age, gender, blood type, BMI)
  - Medical history (chronic conditions, surgeries, family history)
  - Current medications tracking
  - Allergies management (drug, food, environmental)
  - Lifestyle habits (exercise, diet, sleep, stress levels)
- ✅ **RAG-Powered Chat** - Retrieval Augmented Generation with:
  - Sentence transformers for embeddings (`all-MiniLM-L6-v2`)
  - FAISS vector store for semantic search
  - Context-aware responses using user health profile
  - Conversation memory and session management
- ✅ **PDF Document Processing** - Upload and analyze medical documents
- ✅ **Personalized Responses** - AI considers your health profile, allergies, and medications
- ✅ **Session Management** - Save and resume conversations
- ✅ **Healthcare-Focused** - Only answers health-related questions with safety checks
- ✅ **Modern UI** - Responsive design with ChatGPT-like interface

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- MongoDB Atlas (Database)
- JWT (Authentication)
- Groq API (LLM - Llama 3.1 70B)
- Sentence Transformers (Embeddings)
- FAISS (Vector search)
- PyPDF2 (PDF processing)
- Python 3.11

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Jinja2 templates
- Vanilla JavaScript (no frameworks)

---

## 📦 Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **MongoDB Atlas Account** (Free tier) - [Sign up](https://www.mongodb.com/cloud/atlas/register)
- **Groq API Key** (Free tier) - [Get key](https://console.groq.com/)

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/chandureddy031/health_chat_bot.git
cd health_chat_bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file and add your credentials (see Configuration section)

# Run application
python -m backend.main

# Open browser
http://localhost:8000

🪟 Windows Installation
Step 1: Clone the Repository

# Open Command Prompt or PowerShell
cd C:\Users\YourUsername\Documents

# Clone the repository
git clone https://github.com/chandureddy031/health_chat_bot.git

# Navigate into directory
cd health_chat_bot

Step 2: Create Virtual Environment
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt
If activation fails:

PowerShell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
venv\Scripts\activate
Step 3: Install Dependencies
bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements (takes 5-10 minutes)
pip install -r requirements.txt
Step 4: Create Environment File
bash
# Create .env file
type nul > .env

# Open with notepad
notepad .env
Copy the configuration from Configuration section below.

Step 5: Create Required Directories
bash
mkdir backend\documents
mkdir backend\vector_store
Step 6: Run Application
bash
python -m backend.main
Open browser: http://localhost:8000

🍎 macOS/Linux Installation
Step 1: Clone the Repository
bash
# Open Terminal
cd ~/Documents

# Clone the repository
git clone https://github.com/chandureddy031/health_chat_bot.git

# Navigate into directory
cd health_chat_bot
Step 2: Create Virtual Environment
bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt
Step 3: Install Dependencies
bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
On macOS, if you get errors:

bash
# Install Xcode Command Line Tools
xcode-select --install

# Try installing PyTorch separately
pip install torch torchvision torchaudio
Step 4: Create Environment File
bash
# Create .env file
touch .env

# Open with default text editor
open -e .env

# Or use nano
nano .env
Copy the configuration from Configuration section below.

Step 5: Create Required Directories
bash
mkdir -p backend/documents
mkdir -p backend/vector_store
Step 6: Run Application
bash
python -m backend.main
Open browser: http://localhost:8000

⚙️ Configuration
Create a .env file in the project root directory with the following content:

env
# ============================================
# MongoDB Configuration
# ============================================
MONGO_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=healthcare_chatbot

# ============================================
# JWT Configuration
# ============================================
JWT_SECRET_KEY=super-secret-change-me-please-2026-random-long-string-84a2d
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ============================================
# API Keys
# ============================================
GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE

# Optional API Keys (for future features)
SERPER_API_KEY=your_serper_key_here
NEWS_API_KEY=your_news_api_key_here
GEMINI_API_KEY=your_gemini_key_here
🔑 How to Get Your Credentials
1. MongoDB Atlas URI
Go to MongoDB Atlas
Create free account → Create cluster (free M0 tier)
Click "Connect" on your cluster
Select "Connect your application"
Copy connection string
Replace <password> with your database password
Paste into MONGO_URI
Example:

Code
MONGO_URI=mongodb+srv://myuser:MyP@ssw0rd@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
Important: Whitelist your IP in MongoDB Atlas:

Network Access → Add IP Address → Allow Access from Anywhere (0.0.0.0/0)
2. Groq API Key
Visit Groq Console
Sign up for free account
Go to API Keys section
Click "Create API Key"
Copy the key
Paste into GROQ_API_KEY
Example:

Code
GROQ_API_KEY=gsk_abc123xyz456def789ghi012jkl345mno678pqr901stu234vwx567
3. Generate Secure JWT Secret
Windows (PowerShell):

PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | % {[char]$_})
macOS/Linux:

bash
openssl rand -base64 48
Copy the output to JWT_SECRET_KEY.

🏃 Running the Application
Method 1: Direct Python
Activate virtual environment first!

Windows:

bash
venv\Scripts\activate
python -m backend.main
macOS/Linux:

bash
source venv/bin/activate
python -m backend.main
Method 2: Using Uvicorn
bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
Method 3: With Auto-Reload (Development)
bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
Expected Output
Code
2026-01-29 10:00:00 - Main - INFO - 🚀 Healthcare Chatbot starting up...
2026-01-29 10:00:00 - Main - INFO - 📍 Running in: Local
2026-01-29 10:00:01 - Database - INFO - Connecting to MongoDB
2026-01-29 10:00:02 - Database - INFO - MongoDB connection successful
2026-01-29 10:00:03 - Embeddings - INFO - Loading embedding model: all-MiniLM-L6-v2
2026-01-29 10:00:08 - Embeddings - INFO - Loaded 0 chunks from disk
2026-01-29 10:00:08 - Main - INFO - ✅ Application ready!
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Access Application
Open browser: http://localhost:8000

🐳 Docker Deployment
Using Docker Compose (Recommended)
bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop containers
docker-compose down

# View logs
docker-compose logs -f
Using Docker Commands
Build:

bash
docker build -t healthcare-chatbot .
Run (Windows):

bash
docker run -d ^
  --name healthcare_chatbot ^
  -p 8000:8000 ^
  --env-file .env ^
  -v %cd%\backend\documents:/app/backend/documents ^
  -v %cd%\backend\vector_store:/app/backend/vector_store ^
  healthcare-chatbot
Run (macOS/Linux):

bash
docker run -d \
  --name healthcare_chatbot \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/backend/documents:/app/backend/documents \
  -v $(pwd)/backend/vector_store:/app/backend/vector_store \
  healthcare-chatbot
Manage Container:

bash
# View logs
docker logs -f healthcare_chatbot

# Stop container
docker stop healthcare_chatbot

# Start container
docker start healthcare_chatbot

# Remove container
docker rm healthcare_chatbot
📖 Usage Guide
1. Create Account
Navigate to http://localhost:8000
Click "Sign up" link
Fill in:
Username (minimum 3 characters)
Email
Password (minimum 6 characters)
Confirm Password
Click "Sign Up"
You'll be redirected to sign-in page
2. Sign In
Enter your email and password
Click "Sign In"
You'll be redirected to the chat interface
3. Complete Your Health Profile
Click your avatar circle (with your initials) in top-right corner
Select "Health Profile" from dropdown
Fill out each section:
Basic Information:

Full name, date of birth, gender
Blood type, height, weight (calculates BMI automatically)
Phone number
Medical History:

Select chronic conditions (diabetes, hypertension, asthma, etc.)
List past surgeries
Family medical history
Other health conditions
Current Medications:

Click "Add Medication"
Enter medication name, dosage, frequency
What it's prescribed for
Can add multiple medications
Allergies:

Drug allergies (e.g., Penicillin, Aspirin)
Food allergies (e.g., Peanuts, Shellfish)
Other allergies (e.g., Latex, Pollen)
Lifestyle & Habits:

Exercise frequency (none to daily)
Smoking status (never, former, current)
Alcohol consumption (none to heavy)
Average sleep hours
Diet type (omnivore, vegetarian, vegan, etc.)
Stress level (1-10 slider)
Click "Save" on each section
Click "Back to Chat" when done
4. Upload Medical Documents
In chat interface, find "My Documents" section in left sidebar
Click "Upload PDF" button
Select your medical document (.pdf only)
Lab reports
Prescription records
Medical research papers
Health guidelines
Wait for processing (shows progress bar)
Document is now indexed and searchable
5. Chat with AI
The AI will:

✅ Consider your health profile
✅ Reference your uploaded documents
✅ Warn about allergies
✅ Check medication interactions
✅ Provide personalized advice
✅ Remember conversation context
Example Conversations:

Code
You: What should I eat for breakfast?
AI: Given that you have diabetes [from your profile], I recommend...

You: I have a headache, what can I take?
AI: ⚠️ I notice you're allergic to Aspirin [from your profile]. 
    Safe alternatives include...

You: What does my lab report say about cholesterol?
AI: According to your uploaded document "Lab_Report_2024.pdf"...
Question Types:

Symptoms: "What are symptoms of high blood pressure?"
Treatments: "How to treat migraine?"
Medications: "Can I take ibuprofen with metformin?"
Documents: "Summarize my medical report"
Lifestyle: "Best exercises for diabetes?"
Nutrition: "What foods should I avoid?"
6. Session Management
Create New Chat:

Click "+ New Chat" button in left sidebar
Start fresh conversation
Resume Previous Chat:

Click on any session in "Chat History"
Conversation loads with full context
Continue asking follow-up questions
Delete Chat:

Hover over session in sidebar
Click trash icon
Confirm deletion
7. Logout
Click your avatar in top-right
Select "Logout"
Redirected to sign-in page
Your data is saved and secure
📚 API Documentation
Interactive API Docs
Once running, visit:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
Key API Endpoints
Authentication
Code
POST   /api/auth/signup              Register new user
POST   /api/auth/signin              Login and get JWT token
Chat
Code
POST   /api/chat/message             Send message, get AI response
GET    /api/chat/sessions            Get all user chat sessions
GET    /api/chat/session/{id}        Get specific session with messages
DELETE /api/chat/session/{id}        Delete a chat session
Health Profile
Code
GET    /api/profile                  Get complete health profile
POST   /api/profile/basic-info       Save basic information
POST   /api/profile/medical-history  Save medical history
POST   /api/profile/medications      Add medication
DELETE /api/profile/medications/{id} Delete medication
POST   /api/profile/allergies        Save allergies
POST   /api/profile/lifestyle        Save lifestyle information
Document Management
Code
POST   /api/pdf/upload               Upload PDF document
GET    /api/pdf/documents            Get user's uploaded documents
DELETE /api/pdf/document/{id}        Delete document
Utility
Code
GET    /health                       Health check endpoint
Example API Requests
Sign Up:

bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123"
  }'
Sign In:

bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
Send Chat Message:

bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "What are symptoms of diabetes?",
    "session_id": null
  }'
🔧 Troubleshooting
Issue 1: "Module not found" errors
Cause: Virtual environment not activated or dependencies not installed

Solution:

bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
Issue 2: MongoDB Connection Failed
Symptoms:

Code
ERROR - Database - MongoDB connection failed: ...
Solutions:

Check .env file:

Open .env and verify MONGO_URI is correct
Ensure you replaced <password> with actual password
No extra spaces or quotes
Whitelist IP in MongoDB Atlas:

Go to MongoDB Atlas → Network Access
Click "Add IP Address"
Select "Allow Access from Anywhere" (0.0.0.0/0)
Click "Confirm"
Check user permissions:

MongoDB Atlas → Database Access
Ensure user has "Read and write to any database" role
Test connection:

bash
python -c "from pymongo import MongoClient; client = MongoClient('YOUR_MONGO_URI'); client.admin.command('ping'); print('Connected!')"
Issue 3: Port 8000 Already in Use
Symptoms:

Code
ERROR: [Errno 48] Address already in use
Solution 1 - Use different port:

bash
uvicorn backend.main:app --host 0.0.0.0 --port 8080
Then access: http://localhost:8080

Solution 2 - Kill process using port:

Windows:

bash
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
macOS/Linux:

bash
lsof -ti:8000 | xargs kill -9
Issue 4: Groq API Errors
Symptoms:

Code
ERROR - LLM - Failed to get LLM response: ...
Solutions:

Check API key:

Verify GROQ_API_KEY in .env is correct
No extra spaces or quotes
Key should start with gsk_
Check API credits:

Visit Groq Console
Check usage and limits
Test API:

bash
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_GROQ_API_KEY"
Issue 5: Sentence Transformers Download Fails
Symptoms:

Code
ERROR downloading model...
Solutions:

Pre-download model:

bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
Check internet connection

Use proxy if needed:

bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
Issue 6: Virtual Environment Activation Fails
Windows - "cannot be loaded because running scripts is disabled":

PowerShell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
venv\Scripts\activate
macOS/Linux - "Permission denied":

bash
chmod +x venv/bin/activate
source venv/bin/activate
Issue 7: PDF Upload Fails
Solutions:

Check file size (should be < 10MB for best performance)

Ensure directories exist:

bash
# Windows:
mkdir backend\documents
# macOS/Linux:
mkdir -p backend/documents
Check permissions:

bash
# macOS/Linux:
chmod 755 backend/documents
Issue 8: Chat Not Responding
Checklist:

✅ Is server running? (Check terminal)
✅ Is MongoDB connected? (Check logs)
✅ Is Groq API key valid? (Check .env)
✅ Is browser console showing errors? (Press F12)
✅ Is JWT token expired? (Try logging out and back in)
Debug:

bash
# Enable debug logs
# Add to .env:
LOG_LEVEL=DEBUG

# Restart server and check terminal
Issue 9: Frontend Not Loading
Solutions:

Clear browser cache:

Press Ctrl + Shift + Delete
Clear cached images and files
Or hard refresh: Ctrl + F5
Check static files:

bash
# Verify files exist:
ls frontend/static/css/
ls frontend/static/js/
ls frontend/templates/
Check browser console (F12) for errors

Issue 10: Docker Container Issues
Container won't start:

bash
# Check logs
docker logs healthcare_chatbot

# Rebuild image
docker-compose down
docker-compose up --build
Environment variables not loading:

bash
# Verify .env file exists
ls -la .env

# Check Docker can read it
docker-compose config
health_chat_bot/
├── backend/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app entry point
│   ├── auth.py                      # Authentication routes (signup/signin)
│   ├── chat.py                      # Chat endpoints with RAG
│   ├── profile_routes.py            # Health profile management
│   ├── pdf_routes.py                # PDF upload and processing
│   ├── models.py                    # Pydantic data models
│   ├── db.py                        # MongoDB connection
│   ├── logger.py                    # Logging configuration
│   ├── documents/                   # Uploaded PDFs storage (auto-created)
│   ├── vector_store/                # FAISS index storage (auto-created)
│   └── utils/
│       ├── __init__.py
│       ├── security.py              # JWT & bcrypt password hashing
│       ├── llm.py                   # Groq API integration
│       ├── embeddings.py            # Sentence transformers + FAISS
│       ├── pdf_processor.py         # PDF text extraction & chunking
│       └── rag.py                   # RAG logic with user profile context
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── auth.css             # Sign in/up page styles
│   │   │   ├── chat.css             # Chat interface styles
│   │   │   └── profile.css          # Health profile page styles
│   │   └── js/
│   │       ├── auth.js              # Authentication logic
│   │       ├── chat.js              # Chat functionality & WebSocket
│   │       └── profile.js           # Profile form management
│   └── templates/
│       ├── signin.html              # Sign in page
│       ├── signup.html              # Sign up page
│       ├── chat.html                # Main chat interface
│       └── profile.html             # Health profile forms
│
├── .env                             # Environment variables (create this)
├── .gitignore                       # Git ignore rules
├── .dockerignore                    # Docker ignore rules
├── Dockerfile                       # Docker image configuration
├── docker-compose.yml               # Docker Compose setup
├── requirements.txt                 # Python dependencies
└── README.md                        # This file

Key Files Explained
Backend:

main.py - FastAPI application, routes, middleware
auth.py - User registration, login, JWT token generation
chat.py - Chat message handling, session management
profile_routes.py - CRUD operations for health profiles
pdf_routes.py - File upload, PDF processing
utils/rag.py - Core RAG logic, combines user profile + documents + LLM
utils/embeddings.py - Vector store using FAISS and sentence transformers
utils/llm.py - Groq API client for LLM responses
utils/security.py - Password hashing, JWT creation/validation
Frontend:

chat.html - Main UI with sidebar, message area, input box
chat.js - Handles sending messages, loading sessions, PDF uploads
profile.html - Multi-section form for health data
profile.js - Form submission, data loading, medication management
🔒 Security Best Practices
For Development
✅ Use .env for all secrets
✅ Never commit .env to Git
✅ Keep requirements.txt updated
✅ Use virtual environment
✅ Change default JWT secret
For Production
✅ Use strong JWT secret (64+ random characters)
✅ Enable HTTPS/SSL
✅ Set allow_origins to specific domains (not "*")
✅ Whitelist only production server IP in MongoDB
✅ Use environment variables from hosting platform
✅ Enable rate limiting
✅ Set up monitoring and alerts
✅ Regular dependency updates: pip install --upgrade -r requirements.txt
✅ Use production WSGI server (already using Uvicorn)
✅ Implement CORS properly
✅ Add request size limits
✅ Implement API rate limiting
Security Checklist
bash
# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies
pip list --outdated
pip install --upgrade <package_name>

# Scan for secrets in code
pip install detect-secrets
detect-secrets scan
🚀 Performance Tips
Backend Optimization
Pre-download ML models:

bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
Use connection pooling (already configured in MongoDB)

Enable caching:

Add Redis for session caching
Cache LLM responses for common questions
Optimize vector search:

Limit chunk retrieval (k=5 is default)
Use approximate nearest neighbors for large datasets
Frontend Optimization
Minimize JavaScript:

bash
# Install terser
npm install -g terser

# Minify JS files
terser frontend/static/js/chat.js -o frontend/static/js/chat.min.js
Compress CSS:

bash
# Install clean-css
npm install -g clean-css-cli

# Minify CSS
cleancss -o frontend/static/css/chat.min.css frontend/static/css/chat.css
Lazy load images and components

Use browser caching (add cache headers)

🧪 Testing
Run Tests
bash
# Install pytest
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pip install pytest-cov
pytest --cov=backend tests/
Manual Testing Checklist
 User can sign up with valid credentials
 User cannot sign up with duplicate email
 User can sign in with correct password
 User cannot sign in with wrong password
 JWT token is stored in localStorage
 Protected routes require authentication
 User profile loads correctly
 All profile sections can be saved
 Medications can be added and deleted
 PDF upload works and processes correctly
 Chat sends messages and receives responses
 Chat sessions are saved to database
 Previous sessions can be loaded
 Session deletion works
 Logout clears token and redirects
 Non-healthcare questions are blocked
 Allergies are mentioned in responses
 Conversation context is maintained
 Responsive design works on mobile