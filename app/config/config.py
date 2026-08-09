APP_NAME = "DevForge"
APP_VERSION = "0.1.0"
from dotenv import load_dotenv
import os

load_dotenv()

# Use environment variables when provided, otherwise fall back to safe defaults
APP_NAME = os.getenv("APP_NAME", APP_NAME)
APP_VERSION = os.getenv("APP_VERSION", APP_VERSION)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./devforge.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", None)