import os
from dotenv import load_dotenv

load_dotenv()

print("AI_API_KEY:", os.getenv("AI_API_KEY"))
print("AI_MODEL:", os.getenv("AI_MODEL"))
print("AI_API_BASE:", os.getenv("AI_API_BASE"))