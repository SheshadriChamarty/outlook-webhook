import os
from dotenv import load_dotenv

# Force load the .env file
load_dotenv()

# --- AI Configuration ---
# You are using Gemini now, so we need this key.
# (We removed DEEPSEEK_API_KEY since you aren't using it anymore)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- SMTP Configuration (Sending Emails) ---
EMAIL_SERVER = os.getenv("EMAIL_SERVER", "smtp.gmail.com")
EMAIL_PORT = os.getenv("EMAIL_PORT", 587)
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")  # Bot's email address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App Password for SMTP