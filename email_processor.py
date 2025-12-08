from graph_client import GraphClient
from agents.filtering_agent import filter_email
from agents.response_agent import generate_response
from core.email_sender import send_triage_report

graph = GraphClient()

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
    
    Handles both:
    - Direct Graph API response: email_json with direct fields
    - MongoDB stored format: email_json.payload with nested structure
    """
    # Handle MongoDB format (wrapped in 'payload') or direct Graph API format
    if "payload" in email_json:
        email_data = email_json["payload"]
    else:
        email_data = email_json
    
    # Extract email fields
    message_id = email_data.get("id", "")
    subject = email_data.get("subject", "No subject")
    body_content = email_data.get("body", {}).get("content", "")
    
    # Extract sender email (from field)
    sender = ""
    if "from" in email_data and email_data["from"]:
        sender = email_data["from"].get("emailAddress", {}).get("address", "")
    elif "sender" in email_data and email_data["sender"]:
        sender = email_data["sender"].get("emailAddress", {}).get("address", "")
    
    # Extract recipient email (toRecipients - first recipient)
    recipient = ""
    if "toRecipients" in email_data and email_data["toRecipients"]:
        if len(email_data["toRecipients"]) > 0:
            recipient = email_data["toRecipients"][0].get("emailAddress", {}).get("address", "")

    print("🔥 New Email Received")
    print(f"From: {sender}")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print(f"Message ID: {message_id}")
    print(f"Body length: {len(body_content)} characters")
    
    # Validate required fields
    if not subject:
        print("⚠️ Warning: Subject is empty")
    if not body_content:
        print("⚠️ Warning: Body content is empty")
    if not sender:
        print("⚠️ Warning: Sender email is empty - cannot send reply")

    # Convert to format expected by agents
    email_dict = {
        "subject": subject,
        "body": body_content,
        "from": sender
    }

    try:
        # 1. Filter Logic
        print("🔍 Filtering email...")
        classification = filter_email(email_dict)
        print(f"   Classification: {classification}")
        
        if classification == "spam":
            print("   Marked as SPAM, skipping.")
            return {
                "status": "skipped",
                "reason": "spam",
                "classification": classification,
                "subject": subject
            }

        # 2. Generate Triage Report
        print("🤖 Generating AI Triage Report...")
        triage_report = generate_response(email_dict)

        # 3. Send Auto-Reply
        print(f"📧 Sending reply to {sender}...")
        success = send_triage_report(
            original_subject=subject,
            report_body=triage_report,
            target_email=sender
        )

        if success:
            print(f"✅ Email processed successfully: {subject}")
            return {
                "status": "success",
                "subject": subject,
                "classification": classification,
                "ai_report": triage_report
            }
        else:
            print("❌ Failed to send email reply.")
            return {
                "status": "error",
                "subject": subject,
                "error": "Failed to send email reply"
            }

    except Exception as e:
        print(f"❌ Error processing email: {e}")
        return {
            "status": "error",
            "subject": subject,
            "error": str(e)
        }
