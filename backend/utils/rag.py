from typing import List, Dict
from backend.utils.llm import GroqLLM
from backend.utils.embeddings import VectorStore
from backend.logger import get_logger

logger = get_logger("RAG")

class RAGSystem:
    def __init__(self):
        self.llm = GroqLLM()
        self.vector_store = VectorStore()
        
        # Healthcare-focused system prompt
        self.system_prompt = """You are a healthcare assistant specialized in medical information. 

IMPORTANT RULES:
1. PRIMARILY answer questions related to healthcare, medicine, wellness, and medical topics
2. If a user asks about an UPLOADED DOCUMENT (PDF), you may answer questions about that document even if it's not strictly medical
3. If a question is NOT related to healthcare AND there's no uploaded document context, politely decline and say: "I'm a healthcare assistant and can only help with health-related questions."
4. Base your answers on the provided context from documents when available
5. Always remind users to consult healthcare professionals for serious medical concerns
6. Be accurate, empathetic, and clear in your responses
7. If you're unsure, admit it and recommend consulting a doctor

When provided with document context, use it to give accurate, evidence-based answers."""
    
    def is_healthcare_related(self, query: str) -> bool:
        """
        Check if query is healthcare-related using keywords
        
        Args:
            query: User query
            
        Returns:
            True if healthcare-related
        """
        healthcare_keywords = [
            'health', 'medical', 'medicine', 'doctor', 'hospital', 'disease', 
            'symptom', 'treatment', 'diagnosis', 'patient', 'care', 'therapy',
            'drug', 'medication', 'pain', 'injury', 'illness', 'condition',
            'wellness', 'fitness', 'nutrition', 'diet', 'exercise', 'mental health',
            'surgery', 'vaccine', 'infection', 'chronic', 'acute', 'clinic',
            'pharmaceutical', 'healthcare', 'physician', 'nurse', 'medical record',
            'blood', 'heart', 'lung', 'brain', 'cancer', 'diabetes', 'pressure',
            'temperature', 'fever', 'cough', 'headache', 'stomach', 'body'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in healthcare_keywords)
    
    def is_document_query(self, query: str) -> bool:
        """
        Check if query is asking about an uploaded document
        
        Args:
            query: User query
            
        Returns:
            True if asking about document
        """
        document_keywords = [
            'pdf', 'document', 'file', 'upload', 'paper', 'report', 'resume',
            'what does the document', 'what is in the', 'tell me about the',
            'summarize', 'summary', 'what does it say', 'according to',
            'from the file', 'in the pdf', 'the document says',
            'contains', 'about the', 'what is', 'tell me'
        ]
        
        query_lower = query.lower()
        
        # Check for document keywords
        has_doc_keyword = any(keyword in query_lower for keyword in document_keywords)
        
        # If query mentions "document" or "pdf" or "file" -> definitely a doc query
        if any(word in query_lower for word in ['pdf', 'document', 'file', 'resume', 'paper']):
            return True
        
        # Check for question patterns about content
        question_patterns = [
            'what is', 'what are', 'what does', 'tell me', 'show me',
            'contains', 'about', 'summarize', 'summary', 'explain'
        ]
        
        return has_doc_keyword or any(pattern in query_lower for pattern in question_patterns)
    
    def has_user_documents(self, user_id: str) -> bool:
        """
        Check if user has uploaded any documents
        
        Args:
            user_id: User ID
            
        Returns:
            True if user has documents
        """
        user_chunks = [c for c in self.vector_store.chunks if c.get("user_id") == user_id]
        return len(user_chunks) > 0
    
    def generate_response(self, query: str, user_id: str, conversation_history: List[Dict] = None) -> str:
        """
        Generate RAG response with healthcare filtering
        
        Args:
            query: User query
            user_id: User ID for document filtering
            conversation_history: Previous messages in conversation
            
        Returns:
            Generated response
        """
        # Search for relevant document chunks first
        relevant_chunks = self.vector_store.search(query, user_id, k=5)
        has_documents = self.has_user_documents(user_id)
        is_doc_query = self.is_document_query(query)
        is_health_query = self.is_healthcare_related(query)
        
        logger.info(f"Query: '{query}'")
        logger.info(f"Analysis - Healthcare: {is_health_query}, Document Query: {is_doc_query}, Has Docs: {has_documents}, Chunks Found: {len(relevant_chunks)}")
        
        # SIMPLIFIED LOGIC: If user has documents, be very permissive
        if has_documents:
            # Allow almost anything if user has uploaded documents
            # Only block truly inappropriate queries (spam, abuse, etc.)
            inappropriate_keywords = ['hack', 'illegal', 'porn', 'violence']
            if any(word in query.lower() for word in inappropriate_keywords):
                return "I cannot help with that request."
            
            # Allow the query - either health-related or about documents
            logger.info("Query allowed - user has documents")
        elif is_health_query:
            # Allow health queries even without documents
            logger.info("Query allowed - healthcare related")
        else:
            # Block only if no documents and not healthcare
            logger.warning(f"Non-healthcare query blocked: {query}")
            return "I'm a healthcare assistant and can only help with health-related questions. Please ask me about medical topics, symptoms, treatments, wellness, or general health information. 🏥\n\n💡 Tip: Upload medical PDFs to ask questions about them!"
        
        # Build context from retrieved chunks
        context = ""
        if relevant_chunks:
            context = "\n\n--- RELEVANT DOCUMENT EXCERPTS ---\n"
            for idx, chunk in enumerate(relevant_chunks):
                context += f"\n[Source: {chunk['source']}, Section {chunk['chunk_id']+1}]\n{chunk['text']}\n"
            context += "\n--- END OF DOCUMENT EXCERPTS ---\n"
            logger.info(f"Using {len(relevant_chunks)} chunks from documents")
        
        # Build messages for LLM
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current query with context
        if context:
            # If we have document context, emphasize answering from it
            user_message = f"{context}\n\nUser Question: {query}\n\nPlease answer based on the provided document excerpts above. If the document doesn't contain relevant information, use your general knowledge to help."
        else:
            user_message = query
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Generate response
        logger.info(f"Generating RAG response")
        response = self.llm.chat(messages)
        
        # REMOVED: Source attribution
        # No longer adding "Based on: filename" to the response
        
        return response

# Global RAG instance
rag_system = RAGSystem()