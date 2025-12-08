from graph_client import GraphClient
from agents.filtering_agent import filter_email
from agents.response_agent import generate_response
from core.email_sender import send_triage_report
from utils.logger import get_logger

graph = GraphClient()
logger = get_logger(__name__)

def fetch_email(message_id, user_id):
    """Fetches email from Microsoft Graph API."""
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{message_id}"
    response = graph.get(url)
    return response.json()

def process_email(email_json):
    """
    Processes an email received from Outlook webhook:
    1. Filters email (spam check)
    2. Generates AI triage report
    3. Sends auto-reply
    
    This function can be called every time without any tracking or deduplication.
    """
    message_id = email_json.get("id", "")
    subject = email_json.get("subject", "No subject")
    body_content = email_json.get("body", {}).get("content", "")
    sender = email_json.get("from", {}).get("emailAddress", {}).get("address", "")

    logger.info("🔥 New Email Received")
    logger.info(f"From: {sender}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Message ID: {message_id}")

    # Convert to format expected by agents
    email_dict = {
        "subject": subject,
        "body": body_content,
        "from": sender
    }

    try:
        # 1. Filter Logic
        logger.info("🔍 Filtering email...")
        classification = filter_email(email_dict)
        logger.info(f"   Classification: {classification}")
        
        if classification == "spam":
            logger.info("   Marked as SPAM, skipping.")
            return {
                "status": "skipped",
                "reason": "spam",
                "classification": classification,
                "subject": subject
            }

        # 2. Generate Triage Report
        logger.info("🤖 Generating AI Triage Report...")
        triage_report = generate_response(email_dict)

        # 3. Send Auto-Reply
        logger.info(f"📧 Sending reply to {sender}...")
        success = send_triage_report(
            original_subject=subject,
            report_body=triage_report,
            target_email=sender
        )

        if success:
            logger.info(f"✅ Email processed successfully: {subject}")
            return {
                "status": "success",
                "subject": subject,
                "classification": classification,
                "ai_report": triage_report
            }
        else:
            logger.error("❌ Failed to send email reply.")
            return {
                "status": "error",
                "subject": subject,
                "error": "Failed to send email reply"
            }

    except Exception as e:
        logger.error(f"❌ Error processing email: {e}")
        return {
            "status": "error",
            "subject": subject,
            "error": str(e)
        }
