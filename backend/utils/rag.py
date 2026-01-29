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
    
    def get_user_info(self, user_id: str) -> Dict:
        """Get user basic info (name, email) from users collection"""
        try:
            db = Database.get_db()
            users_collection = db["users"]
            user = users_collection.find_one({"_id": user_id})
            
            if user:
                return {
                    "username": user.get("username", ""),
                    "email": user.get("email", "")
                }
            return {}
        except Exception as e:
            logger.error(f"Error loading user info: {e}")
            return {}
    
    def get_user_profile_context(self, user_id: str) -> str:
        """
        Get user health profile from database and format as context
        """
        try:
            db = Database.get_db()
            profiles_collection = db["user_profiles"]
            
            profile = profiles_collection.find_one({"user_id": user_id})
            
            if not profile:
                return ""
            
            context_parts = ["\n=== PATIENT HEALTH PROFILE ==="]
            
            # Basic Info
            if profile.get("basic_info"):
                basic = profile["basic_info"]
                if basic.get('full_name'):
                    context_parts.append(f"Patient Name: {basic['full_name']}")
                if basic.get('date_of_birth'):
                    from datetime import datetime
                    dob = basic['date_of_birth']
                    try:
                        birth_year = int(dob.split('-')[0])
                        age = datetime.now().year - birth_year
                        context_parts.append(f"Age: {age} years old (DOB: {dob})")
                    except:
                        context_parts.append(f"Date of Birth: {dob}")
                if basic.get('gender'):
                    context_parts.append(f"Gender: {basic['gender']}")
                if basic.get('blood_type'):
                    context_parts.append(f"Blood Type: {basic['blood_type']}")
                if basic.get('height') and basic.get('weight'):
                    height = basic['height']
                    weight = basic['weight']
                    bmi = round(weight / ((height/100) ** 2), 1)
                    bmi_category = "Normal"
                    if bmi < 18.5:
                        bmi_category = "Underweight"
                    elif bmi >= 25 and bmi < 30:
                        bmi_category = "Overweight"
                    elif bmi >= 30:
                        bmi_category = "Obese"
                    context_parts.append(f"Height: {height}cm, Weight: {weight}kg, BMI: {bmi} ({bmi_category})")
            
            # Medical History
            if profile.get("medical_history"):
                medical = profile["medical_history"]
                if medical.get('chronic_conditions') and len(medical['chronic_conditions']) > 0:
                    context_parts.append(f"\n⚕️ CHRONIC CONDITIONS: {', '.join(medical['chronic_conditions'])}")
                if medical.get('past_surgeries'):
                    context_parts.append(f"Past Surgeries: {medical['past_surgeries']}")
                if medical.get('family_history'):
                    context_parts.append(f"Family History: {medical['family_history']}")
                if medical.get('other_conditions'):
                    context_parts.append(f"Other Conditions: {medical['other_conditions']}")
            
            # Medications
            if profile.get("medications") and len(profile["medications"]) > 0:
                meds = profile["medications"]
                context_parts.append(f"\n💊 CURRENT MEDICATIONS:")
                for med in meds:
                    med_info = f"  - {med['medication_name']} ({med['dosage']}, {med['frequency']})"
                    if med.get('prescribed_for'):
                        med_info += f" for {med['prescribed_for']}"
                    context_parts.append(med_info)
            
            # Allergies - CRITICAL
            if profile.get("allergies"):
                allergies = profile["allergies"]
                allergy_items = []
                if allergies.get('drug_allergies') and allergies['drug_allergies'].strip():
                    allergy_items.append(f"Drugs: {allergies['drug_allergies']}")
                if allergies.get('food_allergies') and allergies['food_allergies'].strip():
                    allergy_items.append(f"Foods: {allergies['food_allergies']}")
                if allergies.get('other_allergies') and allergies['other_allergies'].strip():
                    allergy_items.append(f"Other: {allergies['other_allergies']}")
                
                if allergy_items:
                    context_parts.append(f"\n⚠️ ALLERGIES (CRITICAL):")
                    for item in allergy_items:
                        context_parts.append(f"  - {item}")
            
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
                if lifestyle.get('sleep_hours'):
                    lifestyle_info.append(f"Sleep: {lifestyle['sleep_hours']} hours/night")
                if lifestyle.get('diet_type'):
                    lifestyle_info.append(f"Diet: {lifestyle['diet_type']}")
                if lifestyle.get('stress_level'):
                    lifestyle_info.append(f"Stress Level: {lifestyle['stress_level']}/10")
                
                if lifestyle_info:
                    context_parts.append(f"\n🏃 LIFESTYLE:")
                    for item in lifestyle_info:
                        context_parts.append(f"  - {item}")
            
            context_parts.append("=== END PATIENT PROFILE ===\n")
            
            return '\n'.join(context_parts)
            
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            return ""
    
    def build_system_prompt(self, user_profile_context: str, user_name: str = "") -> str:
        """Build system prompt with user profile"""
        
        greeting = f"You are a helpful healthcare assistant"
        if user_name:
            greeting += f" speaking with {user_name}"
        
        base_prompt = f"""{greeting}. You provide accurate health information in a warm, conversational manner.

PERSONALITY & TONE:
- Be friendly, warm, and empathetic
- Use natural, conversational language
- Address the user by name when appropriate
- Respond to greetings warmly (hi, hello, how are you, etc.)
- Show genuine care and interest
- Be encouraging and supportive

CONVERSATION GUIDELINES:
1. Respond naturally to greetings and casual conversation
2. Answer health and wellness questions with accurate information
3. Provide personalized advice based on the patient's profile
4. ALWAYS check for allergies before recommending anything
5. Consider medications, conditions, and lifestyle when advising
6. For serious concerns, recommend consulting healthcare professionals
7. Be conversational - you can chat about health topics naturally

IMPORTANT SAFETY RULES:
- If the patient has allergies, NEVER recommend those allergens
- If recommending medications, check for interactions with current meds
- Always encourage consulting doctors for diagnoses and serious issues
- Be extra careful with vulnerable populations (pregnant, elderly, children)"""

        if user_profile_context:
            base_prompt += f"\n\n{user_profile_context}"
            base_prompt += """\n\nPERSONALIZATION INSTRUCTIONS:
- Reference the patient's name, conditions, and profile naturally in conversation
- When giving advice, consider their specific health situation
- If they have chronic conditions, factor that into recommendations
- If they're on medications, check for interactions
- If they have allergies, ALWAYS mention and avoid those allergens
- Use their lifestyle info (diet, exercise) to give relevant advice"""
        else:
            base_prompt += "\n\n💡 NOTE: This patient hasn't completed their health profile yet. Encourage them to do so for personalized advice."
        
        return base_prompt
    
    def is_greeting_or_casual(self, query: str) -> bool:
        """Check if query is a greeting or casual conversation"""
        casual_patterns = [
            'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
            'how are you', 'whats up', "what's up", 'sup', 'yo',
            'thank you', 'thanks', 'thank', 'appreciate',
            'bye', 'goodbye', 'see you', 'take care', 'later',
            'ok', 'okay', 'alright', 'got it', 'understood',
            'yes', 'yeah', 'yep', 'no', 'nope',
            'help', 'what can you do', 'who are you', 'introduce yourself'
        ]
        
        query_lower = query.lower().strip()
        
        # Check for exact matches or contains patterns
        for pattern in casual_patterns:
            if query_lower == pattern or (len(query_lower.split()) <= 4 and pattern in query_lower):
                return True
        
        return False
    
    def is_healthcare_related(self, query: str) -> bool:
        """Check if query is healthcare-related - VERY PERMISSIVE"""
        # If it's short and casual, let it through
        if len(query.split()) <= 5:
            return True
        
        healthcare_keywords = [
            # General health
            'health', 'medical', 'medicine', 'doctor', 'hospital', 'clinic',
            # Conditions
            'disease', 'symptom', 'condition', 'illness', 'disorder', 'syndrome',
            # Treatment
            'treatment', 'therapy', 'cure', 'remedy', 'healing',
            # Diagnosis
            'diagnosis', 'test', 'scan', 'exam', 'checkup',
            # Care
            'care', 'patient', 'nurse', 'physician',
            # Medications
            'drug', 'medication', 'pill', 'prescription', 'dose',
            # Body & symptoms
            'pain', 'ache', 'hurt', 'sore', 'injury', 'wound',
            'fever', 'temperature', 'cough', 'sneeze', 'cold', 'flu',
            'headache', 'migraine', 'dizzy', 'nausea', 'vomit',
            'stomach', 'abdomen', 'chest', 'back', 'neck',
            'blood', 'pressure', 'heart', 'pulse', 'breath',
            # Wellness
            'wellness', 'fitness', 'exercise', 'workout', 'yoga',
            'nutrition', 'diet', 'food', 'eat', 'meal', 'vitamin',
            'sleep', 'rest', 'tired', 'fatigue', 'energy',
            'stress', 'anxiety', 'mental', 'depression', 'mood',
            # Body parts
            'head', 'brain', 'eye', 'ear', 'nose', 'throat',
            'lung', 'liver', 'kidney', 'skin', 'bone', 'muscle',
            # Specific conditions
            'cancer', 'diabetes', 'asthma', 'hypertension', 'cholesterol',
            'allergy', 'infection', 'virus', 'bacteria',
            # Life stages
            'pregnant', 'pregnancy', 'baby', 'child', 'elderly', 'age',
            # General wellness questions
            'should i', 'can i', 'is it safe', 'how do i', 'what if'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in healthcare_keywords)
    
    def is_document_query(self, query: str) -> bool:
        """Check if asking about documents"""
        doc_keywords = ['pdf', 'document', 'file', 'upload', 'report', 'summarize', 'what does']
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in doc_keywords)
    
    def has_user_documents(self, user_id: str) -> bool:
        """Check if user has documents"""
        user_chunks = [c for c in self.vector_store.chunks if c.get("user_id") == user_id]
        return len(user_chunks) > 0
    
    def generate_response(
        self, 
        query: str, 
        user_id: str, 
        session_id: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Generate personalized response
        """
        # Load user info and profile
        user_info = self.get_user_info(user_id)
        user_name = user_info.get('username', '')
        user_profile_context = self.get_user_profile_context(user_id)
        
        # Check query type
        is_greeting = self.is_greeting_or_casual(query)
        is_health = self.is_healthcare_related(query)
        is_doc_query = self.is_document_query(query)
        has_docs = self.has_user_documents(user_id)
        has_profile = bool(user_profile_context)
        
        # Search documents if relevant
        relevant_chunks = []
        if has_docs and (is_health or is_doc_query):
            relevant_chunks = self.vector_store.search(query, user_id, k=3)
        
        logger.info(f"[{session_id}] User: {user_name}, Query: '{query}'")
        logger.info(f"[{session_id}] Greeting: {is_greeting}, Health: {is_health}, Docs: {len(relevant_chunks)}, Profile: {has_profile}")
        
        # VERY PERMISSIVE - allow almost everything
        if not is_greeting and not is_health and not is_doc_query and not has_docs:
            # Only block truly inappropriate content
            spam_keywords = ['hack', 'crack', 'illegal', 'porn', 'xxx', 'violence', 'weapon']
            if any(word in query.lower() for word in spam_keywords):
                return "I can't help with that. Please ask health-related questions."
            
            # Otherwise, try to redirect gently
            logger.info(f"[{session_id}] Borderline query - allowing with gentle redirect")
        
        # Build document context
        document_context = ""
        if relevant_chunks:
            document_context = "\n=== RELEVANT MEDICAL DOCUMENTS ===\n"
            for chunk in relevant_chunks:
                document_context += f"\n[{chunk['source']}]\n{chunk['text']}\n"
            document_context += "=== END DOCUMENTS ===\n"
        
        # Build system prompt with user info
        system_prompt = self.build_system_prompt(user_profile_context, user_name)
        
        # Build conversation
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent history (last 8 messages = 4 exchanges)
        if conversation_history and len(conversation_history) > 0:
            recent = conversation_history[-8:]
            for msg in recent:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            logger.info(f"[{session_id}] Added {len(recent)} history messages")
        
        # Add current query
        if document_context:
            user_message = f"{document_context}\n\nUser: {query}"
        else:
            user_message = query
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Generate response
        logger.info(f"[{session_id}] Sending to LLM with {len(messages)} messages")
        response = self.llm.chat(messages)
        
        logger.info(f"[{session_id}] Response generated: {response[:100]}...")
        return response

rag_system = RAGSystem()