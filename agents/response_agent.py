from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from ai_config import GOOGLE_API_KEY
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "no_file"
def generate_response(email: dict) -> str:
    """
    Analyzes the email and generates a Workday/HRIT Triage Report.
    """
    
    # 1. Define the Strict Triage Prompt
    prompt_template = PromptTemplate(
        input_variables=["subject", "content"],
        template=(
            "You are an assistant that triages Workday Community emails for an HRIT/Workday team.\n"
            "Analyze the following email and generate a structured report.\n\n"
            
            "EMAIL DETAILS:\n"
            "Subject: {subject}\n"
            "Content: {content}\n\n"
            
            "INSTRUCTIONS:\n"
            "1. Summarize the issue in <= 4 bullet points.\n"
            "2. Classify IMPACT_LEVEL as HIGH, MEDIUM, or LOW based on these rules:\n"
            "   - HIGH: security vulnerabilities, production incidents, mandatory changes impacting existing behavior/compliance, breaking changes < 30 days.\n"
            "   - MEDIUM: upcoming changes requiring config/testing, effective > 30 days out.\n"
            "   - LOW: informational updates, optional features, marketing, irrelevant items.\n"
            "3. Classify MODULE (e.g., HCM, Payroll, Financials, Security, Integrations) and likely WORKSTREAM_OWNER.\n"
            "4. Suggest ACTION in 1-2 sentences.\n\n"
            
            "OUTPUT FORMAT:\n"
            "SUMMARY:\n"
            "- [Point 1]\n"
            "- [Point 2]\n\n"
            "IMPACT_LEVEL: [Level]\n"
            "MODULE/OWNER: [Module] / [Owner]\n"
            "SUGGESTED ACTION: [Action]"
        )
    )
    
    prompt = prompt_template.format(
        subject=email.get("subject", ""),
        content=email.get("body", "")
    )
    
    # 2. Initialize Gemini (Using the Lite model for speed/quota safety)
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite", 
        temperature=0.0,
        google_api_key=GOOGLE_API_KEY,
        transport="rest"  
    )
    
    # 3. Generate Report
    try:
        response = model.invoke(prompt)
        report_text = response.content if hasattr(response, "content") else str(response)
        return report_text.strip()
    except Exception as e:
        return f"Error generating report: {str(e)}"