# bot/palmai.py

import os
import google.generativeai as palm
from dotenv import load_dotenv

load_dotenv('.env')

class Palmai:
    _instance = None  

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Palmai, cls).__new__(cls)
            cls._instance._initialize_palm()
        return cls._instance

    def _initialize_palm(self):
        api_key = os.getenv('PALM_API_KEY')
        palm.configure(api_key=api_key)

    def generate_chat(self, user_input):
        messages = [user_input]
        defaults = self._get_default_chat_params()
        response = palm.chat(
            **defaults,
            context=None,
            examples=None,
            messages=messages,
        )
        return response.last

    def generate_text(self, user_input):
        defaults = self._get_default_text_params()
        response = palm.generate_text(
            **defaults,
            prompt=user_input,
        )
        return response.result

    def reset(self):
        """Reset the PalmAI instance, allowing re-initialization."""
        self.__class__._instance = None

    def _get_default_chat_params(self):
        return {
            'model': 'models/chat-bison-001',  # Chat-optimized generative language model.
            'temperature': 0.45,
            'candidate_count': 1,
            'top_k': 45,
            'top_p': 0.85,
        }

    def _get_default_text_params(self):
        return {
            'model': 'models/text-bison-001',  # Model targeted for text generation.
            'temperature': 0.75,
            'candidate_count': 1,
            'top_k': 35,
            'top_p': 0.65,
            'max_output_tokens': 1024,
            'stop_sequences': [],
        }

palm_instance = Palmai()
