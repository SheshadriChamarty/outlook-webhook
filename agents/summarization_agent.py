from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from ai_config import GOOGLE_API_KEY
# from langchain_openai import ChatOpenAI
from utils.formatter import clean_text



def summarize_email(email: dict) -> str:
    """
    Uses an LLM to generate a concise summary of the email content.
    """
    prompt_template = PromptTemplate(
        input_variables=["content"],
        template="Summarize the following email content in 2 to 3 sentences: {content}"
    )
    
    prompt = prompt_template.format(content=email.get("body", ""))
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.0,
        google_api_key=GOOGLE_API_KEY
    )# Initialize the model with Deepseek's configurations
    
    
    summary = model.invoke(prompt)
    summary_text = summary.content if hasattr(summary, "content") else str(summary)
    
    
    return clean_text(summary_text)