import smtplib
from email.message import EmailMessage
from ai_config import EMAIL_SERVER, EMAIL_PASSWORD, EMAIL_USERNAME, EMAIL_PORT
from utils.logger import get_logger
from utils.formatter import clean_text

logger = get_logger(__name__)

def send_triage_report(original_subject: str, report_body: str, target_email: str) -> bool:
    """
    Sends an AI-generated triage report as an email reply.
    
    Args:
        original_subject: Original email subject
        report_body: AI-generated report content
        target_email: Recipient email address
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        msg = EmailMessage()
        
        clean_subj = clean_text(original_subject)
        if not clean_subj.lower().startswith("re:"):
            msg["Subject"] = f"Re: {clean_subj} [AI Analysis]"
        else:
            msg["Subject"] = clean_subj

        msg["From"] = EMAIL_USERNAME
        msg["To"] = target_email
        
        intro = "Here is the automated Workday/HRIT analysis of your request:\n\n"
        full_body = intro + report_body
        
        msg.set_content(full_body)
        
        logger.debug(f"Connecting to SMTP server {EMAIL_SERVER}:{EMAIL_PORT}")
        with smtplib.SMTP(EMAIL_SERVER, int(EMAIL_PORT)) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
            logger.info(f"✅ Reply sent successfully to {target_email}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to reply: {e}")
        return False
