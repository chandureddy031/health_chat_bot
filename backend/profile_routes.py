from fastapi import APIRouter, Depends, HTTPException, status
from backend.db import Database
from backend.utils.security import verify_token
from backend.logger import get_logger
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

logger = get_logger("ProfileRoutes")
router = APIRouter(prefix="/api/profile", tags=["User Profile"])

# Pydantic Models
class BasicInfo(BaseModel):
    full_name: str
    date_of_birth: str
    gender: str
    blood_type: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    phone: Optional[str] = None

class MedicalHistory(BaseModel):
    chronic_conditions: List[str] = []
    past_surgeries: Optional[str] = None
    family_history: Optional[str] = None
    other_conditions: Optional[str] = None

class Allergies(BaseModel):
    drug_allergies: Optional[str] = None
    food_allergies: Optional[str] = None
    other_allergies: Optional[str] = None

class Lifestyle(BaseModel):
    exercise_frequency: Optional[str] = None
    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    sleep_hours: Optional[int] = None
    diet_type: Optional[str] = None
    stress_level: Optional[int] = None

class Medication(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    prescribed_for: Optional[str] = None

@router.get("")
async def get_profile(user_email: str = Depends(verify_token)):
    """Get complete user health profile"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        profiles_collection = db["user_profiles"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        # Get profile or return empty
        profile = profiles_collection.find_one({"user_id": user_id})
        
        if not profile:
            return {
                "user_id": user_id,
                "basic_info": None,
                "medical_history": None,
                "medications": [],
                "allergies": None,
                "lifestyle": None
            }
        
        profile["_id"] = str(profile["_id"])
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )

@router.post("/basic-info")
async def save_basic_info(
    basic_info: BasicInfo,
    user_email: str = Depends(verify_token)
):
    """Save basic information"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        profiles_collection = db["user_profiles"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        # Update or create profile
        profiles_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "basic_info": basic_info.dict(),
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        logger.info(f"Basic info saved for user: {user_email}")
        return {"message": "Basic information saved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save basic info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save basic information"
        )

@router.post("/medical-history")
async def save_medical_history(
    medical_history: MedicalHistory,
    user_email: str = Depends(verify_token)
):
    """Save medical history"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        profiles_collection = db["user_profiles"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        profiles_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "medical_history": medical_history.dict(),
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        logger.info(f"Medical history saved for user: {user_email}")
        return {"message": "Medical history saved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save medical history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save medical history"
        )

@router.post("/allergies")
async def save_allergies(
    allergies: Allergies,
    user_email: str = Depends(verify_token)
):
    """Save allergies"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        profiles_collection = db["user_profiles"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        profiles_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "allergies": allergies.dict(),
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        logger.info(f"Allergies saved for user: {user_email}")
        return {"message": "Allergies saved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save allergies error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save allergies"
        )

@router.post("/lifestyle")
async def save_lifestyle(
    lifestyle: Lifestyle,
    user_email: str = Depends(verify_token)
):
    """Save lifestyle information"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        profiles_collection = db["user_profiles"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        profiles_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "lifestyle": lifestyle.dict(),
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        logger.info(f"Lifestyle saved for user: {user_email}")
        return {"message": "Lifestyle information saved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save lifestyle error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save lifestyle information"
        )

@router.post("/medications")
async def add_medication(
    medication: Medication,
    user_email: str = Depends(verify_token)
):
    """Add a medication"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        profiles_collection = db["user_profiles"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        profiles_collection.update_one(
            {"user_id": user_id},
            {
                "$push": {"medications": medication.dict()},
                "$set": {"updated_at": datetime.utcnow()},
                "$setOnInsert": {
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        logger.info(f"Medication added for user: {user_email}")
        return {"message": "Medication added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add medication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add medication"
        )

@router.delete("/medications/{index}")
async def delete_medication(
    index: int,
    user_email: str = Depends(verify_token)
):
    """Delete a medication by index"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        profiles_collection = db["user_profiles"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        # Get profile
        profile = profiles_collection.find_one({"user_id": user_id})
        if not profile or "medications" not in profile:
            raise HTTPException(status_code=404, detail="No medications found")
        
        # Remove medication at index
        medications = profile["medications"]
        if index < 0 or index >= len(medications):
            raise HTTPException(status_code=404, detail="Medication not found")
        
        medications.pop(index)
        
        profiles_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "medications": medications,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Medication deleted for user: {user_email}")
        return {"message": "Medication deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete medication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete medication"
        )