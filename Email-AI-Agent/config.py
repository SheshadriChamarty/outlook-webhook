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
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME") # This is your personal mail (The Bot)
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") # Your App Password

# --- IMAP Configuration (Reading Emails) ---
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = os.getenv("IMAP_PORT", 993)
IMAP_USERNAME = os.getenv("IMAP_USERNAME", EMAIL_USERNAME)
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD", EMAIL_PASSWORD)

# --- Triage Configuration ---
# Where should the bot send the reports? 
# You can put your same personal email here to send the report to yourself.
TARGET_PERSONAL_EMAIL = os.getenv("TARGET_PERSONAL_EMAIL", EMAIL_USERNAME)