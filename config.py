import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")

# App directories
DB_DIR = BASE_DIR / "database"
ASSETS_DIR = BASE_DIR / "assets"
EXPORTS_DIR = BASE_DIR / "exports"

# Ensure all directories exist
DB_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Database configuration
DB_PATH = DB_DIR / "health.db"

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or ""

def configure_gemini(api_key=None):
    """
    Configure the Google GenerativeAI API.
    """
    key = api_key or GEMINI_API_KEY
    if key and key.strip():
        genai.configure(api_key=key.strip())
        return True
    return False

# Attempt configuration
HAS_GEMINI_API = configure_gemini()
