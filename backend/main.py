import warnings
warnings.filterwarnings("ignore")

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

from backend.auth import router as auth_router
from backend.chat import router as chat_router
from backend.pdf_routes import router as pdf_router
from backend.profile_routes import router as profile_router  # ADD THIS
from backend.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger("Main")

# Create FastAPI app
app = FastAPI(
    title="Healthcare Chatbot API",
    description="AI-powered healthcare chatbot with RAG and PDF support",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(pdf_router)
app.include_router(profile_router)  # ADD THIS

# Frontend routes
@app.get("/")
async def root():
    """Redirect to signin page"""
    return RedirectResponse(url="/signin")

@app.get("/signin")
async def signin_page(request: Request):
    """Render signin page"""
    return templates.TemplateResponse("signin.html", {"request": request})

@app.get("/signup")
async def signup_page(request: Request):
    """Render signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/chat")
async def chat_page(request: Request):
    """Render chat page"""
    return templates.TemplateResponse("chat.html", {"request": request})

# ADD THIS PROFILE ROUTE
@app.get("/profile")
async def profile_page(request: Request):
    """Render profile page"""
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": "docker" if os.path.exists("/.dockerenv") else "local"
    }

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Healthcare Chatbot starting up...")
    logger.info(f"📍 Running in: {'Docker' if os.path.exists('/.dockerenv') else 'Local'}")
    logger.info("✅ Application ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 Healthcare Chatbot shutting down...")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Healthcare Chatbot application with RAG...")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )