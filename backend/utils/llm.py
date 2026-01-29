import os
from groq import Groq
from backend.logger import get_logger

logger = get_logger("LLM")

class GroqLLM:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        self.model = "llama-3.1-8b-instant"
    
    def chat(self, messages: list) -> str:
        """
        Send chat messages to Groq API and get response
        """
        try:
            logger.info(f"Sending request to GROQ API with model: {self.model}")

            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )

            response = chat_completion.choices[0].message.content
            logger.info("LLM response generated successfully")
            return response

        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise RuntimeError("Failed to get LLM response") from e
