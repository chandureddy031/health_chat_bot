from fastapi import APIRouter, Depends, HTTPException, status
from backend.models import ChatRequest, ChatResponse
from backend.db import Database
from backend.utils.security import verify_token
from backend.utils.rag import rag_system
from backend.logger import get_logger
from datetime import datetime
from bson import ObjectId
from typing import List

logger = get_logger("Chat")
router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    user_email: str = Depends(verify_token)
):
    """Send a message and get RAG-enhanced LLM response"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        sessions_collection = db["chat_sessions"]
        
        # Get user
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # CRITICAL FIX: Keep as ObjectId for profile lookup, convert to string for session
        user_object_id = user["_id"]
        user_id_str = str(user_object_id)
        
        # Create or get session
        if chat_request.session_id:
            session = sessions_collection.find_one({
                "_id": ObjectId(chat_request.session_id),
                "user_id": user_id_str
            })
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            session_id = chat_request.session_id
        else:
            session_id = str(ObjectId())
            session = {
                "_id": ObjectId(session_id),
                "user_id": user_id_str,
                "title": chat_request.message[:50],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "messages": []
            }
            sessions_collection.insert_one(session)
        
        # Get conversation history
        conversation_history = session.get("messages", [])
        
        # CRITICAL: Pass user_id_str for profile lookup
        assistant_response = rag_system.generate_response(
            query=chat_request.message,
            user_id=user_id_str,
            session_id=session_id,
            conversation_history=conversation_history
        )
        
        # Save messages
        user_message = {
            "role": "user",
            "content": chat_request.message,
            "timestamp": datetime.utcnow()
        }
        
        assistant_message = {
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.utcnow()
        }
        
        sessions_collection.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$push": {
                    "messages": {"$each": [user_message, assistant_message]}
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return ChatResponse(
            response=assistant_response,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Keep the rest of the routes the same...
@router.get("/sessions", response_model=List[dict])
async def get_sessions(user_email: str = Depends(verify_token)):
    """Get all chat sessions for the user"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        sessions_collection = db["chat_sessions"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        sessions = list(sessions_collection.find(
            {"user_id": user_id},
            {"messages": 0}
        ).sort("updated_at", -1))
        
        for session in sessions:
            session["id"] = str(session.pop("_id"))
        
        return sessions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sessions"
        )

@router.get("/session/{session_id}", response_model=dict)
async def get_session(
    session_id: str,
    user_email: str = Depends(verify_token)
):
    """Get a specific chat session with messages"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        sessions_collection = db["chat_sessions"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        session = sessions_collection.find_one({
            "_id": ObjectId(session_id),
            "user_id": user_id
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session["id"] = str(session.pop("_id"))
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch session"
        )

@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    user_email: str = Depends(verify_token)
):
    """Delete a chat session"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        sessions_collection = db["chat_sessions"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        result = sessions_collection.delete_one({
            "_id": ObjectId(session_id),
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )