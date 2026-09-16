"""
Utility script to list all available Google Gemini models supporting the 'generateContent' method
for the configured API key.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API with the retrieved key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

print("--- Available Models for Your Key ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error during model query: {e}")
print("-------------------------------------")