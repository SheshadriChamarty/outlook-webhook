from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from ai_config import GOOGLE_API_KEY
from utils.formatter import clean_text
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "no_file"

def filter_email(email: dict) -> str:
    # 1. Define Prompt
    prompt_template = PromptTemplate(
        input_variables=["subject", "content"],
        template=(
            "Classify this email as 'spam', 'urgent', 'informational', or 'needs review'.\n"
            "Subject: {subject}\n"
            "Content: {content}"
        )
    )
    
    prompt = prompt_template.format(
        subject=email.get("subject", ""),
        content=email.get("body", "")[:3000]
    )
    
    # 2. Initialize Model with FORCE REST and TIMEOUT
    # transport="rest" fixes the freezing on Windows/Corporate networks
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.0,
        google_api_key=GOOGLE_API_KEY,
        max_retries=1,
        transport="rest",
        timeout=15.0 # Force crash after 15 seconds if stuck
    )

    print("   ... (Debug: STARTING FILTERING - REST MODE...)")
    
    try:
        classification_result = model.invoke(prompt) 
        text = clean_text(str(classification_result.content)).lower()
        print(f"   ... (Debug: Result -> {text})")
        
        if "needs review" in text: return "needs_review"
        if "urgent" in text: return "urgent"
        if "spam" in text: return "spam"
        return "informational"
        
    except Exception as e:
        print(f"❌ ERROR in Filter: {e}")
        return "informational"