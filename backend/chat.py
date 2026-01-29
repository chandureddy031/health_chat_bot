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
        
        user_id = str(user["_id"])
        
        # Create or get session
        session = None
        if chat_request.session_id:
            session = sessions_collection.find_one({
                "_id": ObjectId(chat_request.session_id),
                "user_id": user_id
            })
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            session_id = chat_request.session_id
            logger.info(f"Continuing existing session: {session_id} with {len(session.get('messages', []))} previous messages")
        else:
            # Create new session
            session_id = str(ObjectId())
            session = {
                "_id": ObjectId(session_id),
                "user_id": user_id,
                "title": chat_request.message[:50],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "messages": []
            }
            sessions_collection.insert_one(session)
            logger.info(f"Created new session: {session_id}")
        
        # Get conversation history - IMPORTANT for context continuity
        conversation_history = session.get("messages", [])
        logger.info(f"Conversation history has {len(conversation_history)} messages")
        
        # Use RAG system with conversation history
        assistant_response = rag_system.generate_response(
            query=chat_request.message,
            user_id=user_id,
            conversation_history=conversation_history  # Pass full history
        )
        
        # Save messages to session
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
                    "messages": {
                        "$each": [user_message, assistant_message]
                    }
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Message processed for session: {session_id}")
        
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
        
        sessions = list(sessions_collection.find(
            {"user_id": str(user["_id"])},
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
        
        session = sessions_collection.find_one({
            "_id": ObjectId(session_id),
            "user_id": str(user["_id"])
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session["id"] = str(session.pop("_id"))
        
        logger.info(f"Loaded session {session_id} with {len(session.get('messages', []))} messages")
        
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
        
        result = sessions_collection.delete_one({
            "_id": ObjectId(session_id),
            "user_id": str(user["_id"])
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Session deleted: {session_id}")
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )