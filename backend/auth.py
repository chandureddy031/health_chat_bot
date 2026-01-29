from fastapi import APIRouter, HTTPException, status
from backend.models import UserSignUp, UserSignIn, Token, User
from backend.db import Database
from backend.utils.security import hash_password, verify_password, create_access_token
from backend.logger import get_logger
from datetime import datetime

logger = get_logger("Auth")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=dict)
async def signup(user: UserSignUp):
    """Register a new user"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_username = users_collection.find_one({"username": user.username})
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user_dict = {
            "username": user.username,
            "email": user.email,
            "password_hash": hash_password(user.password),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = users_collection.insert_one(user_dict)
        logger.info(f"New user registered: {user.email}")
        
        return {
            "message": "User registered successfully",
            "user_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/signin", response_model=Token)
async def signin(user: UserSignIn):
    """Authenticate user and return JWT token"""
    try:
        db = Database.get_db()
        users_collection = db["users"]

        db_user = users_collection.find_one({"email": user.email})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        

        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        

        access_token = create_access_token(data={"sub": user.email})
        logger.info(f"User signed in: {user.email}")
        
        return Token(access_token=access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signin error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )