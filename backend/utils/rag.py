from typing import List, Dict
from backend.utils.llm import GroqLLM
from backend.utils.embeddings import VectorStore
from backend.db import Database
from backend.logger import get_logger

logger = get_logger("RAG")

class RAGSystem:
    def __init__(self):
        self.llm = GroqLLM()
        self.vector_store = VectorStore()
        
        # Healthcare-focused system prompt
        self.base_system_prompt = """You are a personalized healthcare assistant specialized in medical information."""
    
    def get_user_profile_context(self, user_id: str) -> str:
        """
        Get user health profile from database and format as context
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted profile context string
        """
        try:
            db = Database.get_db()
            profiles_collection = db["user_profiles"]
            
            profile = profiles_collection.find_one({"user_id": user_id})
            
            if not profile:
                return ""
            
            context_parts = ["\n--- USER HEALTH PROFILE ---"]
            
            # Basic Info
            if profile.get("basic_info"):
                basic = profile["basic_info"]
                context_parts.append(f"\nPatient: {basic.get('full_name', 'N/A')}")
                context_parts.append(f"Age/DOB: {basic.get('date_of_birth', 'N/A')}")
                context_parts.append(f"Gender: {basic.get('gender', 'N/A')}")
                if basic.get('blood_type'):
                    context_parts.append(f"Blood Type: {basic['blood_type']}")
                if basic.get('height') and basic.get('weight'):
                    bmi = round(basic['weight'] / ((basic['height']/100) ** 2), 1)
                    context_parts.append(f"Height: {basic['height']}cm, Weight: {basic['weight']}kg (BMI: {bmi})")
            
            # Medical History
            if profile.get("medical_history"):
                medical = profile["medical_history"]
                if medical.get('chronic_conditions'):
                    context_parts.append(f"\nChronic Conditions: {', '.join(medical['chronic_conditions'])}")
                if medical.get('past_surgeries'):
                    context_parts.append(f"Past Surgeries: {medical['past_surgeries']}")
                if medical.get('family_history'):
                    context_parts.append(f"Family History: {medical['family_history']}")
                if medical.get('other_conditions'):
                    context_parts.append(f"Other Conditions: {medical['other_conditions']}")
            
            # Medications
            if profile.get("medications"):
                meds = profile["medications"]
                if meds:
                    med_list = [f"{m['medication_name']} ({m['dosage']}, {m['frequency']})" for m in meds]
                    context_parts.append(f"\nCurrent Medications: {'; '.join(med_list)}")
            
            # Allergies
            if profile.get("allergies"):
                allergies = profile["allergies"]
                allergy_list = []
                if allergies.get('drug_allergies'):
                    allergy_list.append(f"Drugs: {allergies['drug_allergies']}")
                if allergies.get('food_allergies'):
                    allergy_list.append(f"Foods: {allergies['food_allergies']}")
                if allergy_list:
                    context_parts.append(f"\n⚠️ ALLERGIES: {'; '.join(allergy_list)}")
            
            # Lifestyle
            if profile.get("lifestyle"):
                lifestyle = profile["lifestyle"]
                lifestyle_info = []
                if lifestyle.get('exercise_frequency'):
                    lifestyle_info.append(f"Exercise: {lifestyle['exercise_frequency']}")
                if lifestyle.get('smoking_status'):
                    lifestyle_info.append(f"Smoking: {lifestyle['smoking_status']}")
                if lifestyle.get('alcohol_consumption'):
                    lifestyle_info.append(f"Alcohol: {lifestyle['alcohol_consumption']}")
                if lifestyle.get('diet_type'):
                    lifestyle_info.append(f"Diet: {lifestyle['diet_type']}")
                if lifestyle_info:
                    context_parts.append(f"\nLifestyle: {'; '.join(lifestyle_info)}")
            
            context_parts.append("--- END USER PROFILE ---\n")
            
            return '\n'.join(context_parts)
            
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            return ""
    
    def build_system_prompt(self, user_profile_context: str) -> str:
        """Build complete system prompt with user profile"""
        prompt = self.base_system_prompt
        
        if user_profile_context:
            prompt += f"\n\n{user_profile_context}"
            prompt += "\n\nIMPORTANT: Use the patient's profile information above to provide PERSONALIZED advice. Reference their specific conditions, medications, and allergies when relevant."
        
        prompt += """

CRITICAL RULES:
1. ALWAYS consider the patient's medical history, current medications, and allergies when providing advice
2. If the patient has allergies, NEVER recommend anything they're allergic to
3. If the patient is on medications, check for potential interactions
4. ONLY answer healthcare-related questions (medicine, wellness, symptoms, treatments)
5. For non-healthcare questions, politely decline
6. If user asks about uploaded documents, answer based on document context
7. Base your answers on provided context from medical documents when available
8. Always remind users to consult healthcare professionals for serious medical concerns
9. Be accurate, empathetic, and clear in your responses
10. If you're unsure, admit it and recommend consulting a doctor

When answering:
- Reference the patient's specific health conditions when relevant
- Warn about medication interactions if applicable
- Consider their lifestyle factors
- Be especially careful with allergy warnings"""

        return prompt
    
    def is_healthcare_related(self, query: str) -> bool:
        """Check if query is healthcare-related using keywords"""
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
        """Check if query is asking about an uploaded document"""
        document_keywords = [
            'pdf', 'document', 'file', 'upload', 'paper', 'report', 'resume',
            'what does the document', 'what is in the', 'tell me about the',
            'summarize', 'summary', 'what does it say', 'according to',
            'from the file', 'in the pdf', 'the document says',
            'contains', 'about the', 'what is', 'tell me'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in document_keywords)
    
    def has_user_documents(self, user_id: str) -> bool:
        """Check if user has uploaded any documents"""
        user_chunks = [c for c in self.vector_store.chunks if c.get("user_id") == user_id]
        return len(user_chunks) > 0
    
    def generate_response(self, query: str, user_id: str, conversation_history: List[Dict] = None) -> str:
        """
        Generate RAG response with user profile and conversation context
        
        Args:
            query: User query
            user_id: User ID for document filtering and profile loading
            conversation_history: Previous messages in conversation
            
        Returns:
            Generated response
        """
        # Load user profile context
        user_profile_context = self.get_user_profile_context(user_id)
        
        # Search for relevant document chunks
        relevant_chunks = self.vector_store.search(query, user_id, k=5)
        has_documents = self.has_user_documents(user_id)
        is_doc_query = self.is_document_query(query)
        is_health_query = self.is_healthcare_related(query)
        
        logger.info(f"Query: '{query}'")
        logger.info(f"Analysis - Healthcare: {is_health_query}, Document Query: {is_doc_query}, Has Docs: {has_documents}, Chunks Found: {len(relevant_chunks)}")
        logger.info(f"User profile loaded: {bool(user_profile_context)}")
        
        # Decision logic
        if has_documents:
            inappropriate_keywords = ['hack', 'illegal', 'porn', 'violence']
            if any(word in query.lower() for word in inappropriate_keywords):
                return "I cannot help with that request."
            logger.info("Query allowed - user has documents")
        elif is_health_query:
            logger.info("Query allowed - healthcare related")
        else:
            logger.warning(f"Non-healthcare query blocked: {query}")
            if has_documents:
                return "I'm a healthcare assistant. I can help with:\n\n1. Health-related questions (symptoms, treatments, wellness, etc.)\n2. Questions about your uploaded medical documents\n\nPlease ask me about medical topics or your uploaded files. 🏥"
            else:
                return "I'm a healthcare assistant and can only help with health-related questions. Please ask me about medical topics, symptoms, treatments, wellness, or general health information. 🏥\n\n💡 Tip: Upload medical PDFs or complete your health profile for personalized advice!"
        
        # Build context from retrieved chunks
        document_context = ""
        if relevant_chunks:
            document_context = "\n\n--- RELEVANT MEDICAL DOCUMENT EXCERPTS ---\n"
            for idx, chunk in enumerate(relevant_chunks):
                document_context += f"\n[Source: {chunk['source']}, Section {chunk['chunk_id']+1}]\n{chunk['text']}\n"
            document_context += "\n--- END OF DOCUMENT EXCERPTS ---\n"
            logger.info(f"Using {len(relevant_chunks)} chunks from documents")
        
        # Build system prompt with user profile
        system_prompt = self.build_system_prompt(user_profile_context)
        
        # Build messages for LLM
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 6 messages = 3 exchanges for better memory)
        if conversation_history:
            recent_history = conversation_history[-6:]
            for msg in recent_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            logger.info(f"Added {len(recent_history)} messages from conversation history")
        
        # Add current query with document context if available
        if document_context:
            user_message = f"{document_context}\n\nUser Question: {query}\n\nPlease answer based on the provided document excerpts and the patient's health profile."
        else:
            user_message = query
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Generate response
        logger.info(f"Generating RAG response")
        response = self.llm.chat(messages)
        
        return response

# Global RAG instance
rag_system = RAGSystem()