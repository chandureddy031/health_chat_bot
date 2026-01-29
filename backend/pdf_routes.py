from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import List
import os
import shutil
from backend.db import Database
from backend.utils.security import verify_token
from backend.utils.pdf_processor import PDFProcessor
from backend.utils.rag import rag_system
from backend.logger import get_logger
from datetime import datetime
from bson import ObjectId

logger = get_logger("PDFRoutes")
router = APIRouter(prefix="/api/pdf", tags=["PDF Management"])

pdf_processor = PDFProcessor()

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user_email: str = Depends(verify_token)
):
    """Upload and process a PDF file"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Get user
        db = Database.get_db()
        users_collection = db["users"]
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        # Save PDF
        file_path = os.path.join(pdf_processor.upload_dir, f"{user_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"PDF uploaded: {file.filename} for user {user_email}")
        
        # Process PDF
        chunks = pdf_processor.process_pdf(file_path)
        
        # Add to vector store
        rag_system.vector_store.add_documents(chunks, user_id)
        
        # Save metadata to database
        pdf_metadata = {
            "user_id": user_id,
            "filename": file.filename,
            "file_path": file_path,
            "chunks_count": len(chunks),
            "uploaded_at": datetime.utcnow()
        }
        
        db["pdf_documents"].insert_one(pdf_metadata)
        
        return {
            "message": "PDF uploaded and processed successfully",
            "filename": file.filename,
            "chunks_count": len(chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )

@router.get("/documents")
async def get_user_documents(user_email: str = Depends(verify_token)):
    """Get list of uploaded PDFs for user"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        documents = list(db["pdf_documents"].find(
            {"user_id": user_id},
            {"_id": 1, "filename": 1, "chunks_count": 1, "uploaded_at": 1}
        ).sort("uploaded_at", -1))
        
        # Convert ObjectId to string
        for doc in documents:
            doc["id"] = str(doc.pop("_id"))
        
        return documents
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get documents error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch documents"
        )

@router.delete("/document/{document_id}")
async def delete_document(
    document_id: str,
    user_email: str = Depends(verify_token)
):
    """Delete a PDF document"""
    try:
        db = Database.get_db()
        users_collection = db["users"]
        user = users_collection.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user["_id"])
        
        # Find document
        document = db["pdf_documents"].find_one({
            "_id": ObjectId(document_id),
            "user_id": user_id
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file
        if os.path.exists(document["file_path"]):
            os.remove(document["file_path"])
        
        # Delete from vector store
        rag_system.vector_store.delete_user_documents(user_id, document["filename"])
        
        # Delete from database
        db["pdf_documents"].delete_one({"_id": ObjectId(document_id)})
        
        logger.info(f"Document deleted: {document['filename']}")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )