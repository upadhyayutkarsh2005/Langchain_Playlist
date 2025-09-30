import google.generativeai
from google.generativeai import list_models
from dotenv import load_dotenv
load_dotenv()
import os

api_key = os.getenv("GOOGLE_API_KEY")
google.generativeai.configure(api_key=api_key)
for m in list_models():
    print(m.name, m.supported_generation_methods)