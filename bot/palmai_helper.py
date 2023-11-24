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
        defaults = {
            'model': 'models/chat-bison-001', # Chat-optimized generative language model.
            'temperature': 0.55,
            'candidate_count': 1,
            'top_k': 35,
            'top_p': 0.75,
        }
        response = palm.chat(
            **defaults,
            context=None,
            examples=None,
            messages=messages,
        )
        return response.last

    def generate_text(self, user_input):
        defaults = {
        # 'model': 'models/text-bison-recitation-off', # Model targeted for text generation with recitation turned off
        # 'model': 'models/text-bison-safety-off', # Model targeted for text generation with safety turned off.
        # 'model': 'models/text-bison-safety-recitation-off', # Model targeted for text generation with safety and recitation turned off.
        'model': 'models/text-bison-001', # Model targeted for text generation.
        'temperature': 0.75,
        'candidate_count': 1,
        'top_k': 40,
        'top_p': 0.55,
        'max_output_tokens': 1024,
        'stop_sequences': [],
        }
        response = palm.generate_text(
            **defaults,
            prompt=user_input,
        )
        return response.result

    def reset(self):
        """Reset the PalmAI instance, allowing re-initialization."""
        self.__class__._instance = None

palm_instance = Palmai()
