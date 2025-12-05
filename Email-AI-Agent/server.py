# import time
# import sys
# from core.email_imap import fetch_imap_emails
# from core.email_sender import send_triage_report
# from agents.filtering_agent import filter_email
# from agents.response_agent import generate_response
# from utils.logger import get_logger
# from utils.tracker import is_processed, mark_email_as_processed
# from config import IMAP_USERNAME, IMAP_PASSWORD, IMAP_SERVER, EMAIL_USERNAME

# logger = get_logger(__name__)

# # Check every 30 seconds (faster check since we only look at 1 email)
# CHECK_INTERVAL = 30 

# def process_single_email(email):
#     """Handles the logic for a single email."""
#     email_id = email.get("id")
#     subject = email.get("subject", "No Subject")
#     sender = email.get("from", "")

#     # 1. Deduplication Check
#     if is_processed(email_id):
#         # We already processed the latest email, so do nothing.
#         return

#     logger.info(f"⚡ New Email Detected: {subject} | From: {sender}")

#     # 2. Safety Check (Don't reply to yourself)
#     if EMAIL_USERNAME in sender:
#         logger.info("Skipping self-sent email.")
#         mark_email_as_processed(email_id)
#         return

#     # 3. Filter Check
#     classification = filter_email(email)
#     logger.info(f"   Classification: {classification}")
    
#     if classification == "spam":
#         logger.info("   Marking as SPAM and skipping.")
#         mark_email_as_processed(email_id)
#         return

#     # 4. Generate Report
#     logger.info("   Generating Triage Report...")
#     triage_report = generate_response(email)

#     # 5. Send Auto-Reply
#     logger.info(f"   🚀 Sending reply to {sender}...")
#     success = send_triage_report(
#         original_subject=subject,
#         report_body=triage_report,
#         target_email=sender
#     )

#     if success:
#         logger.info(f"   ✅ Done! Marking {email_id} as processed.")
#         mark_email_as_processed(email_id)
#     else:
#         logger.error("   ❌ Failed to send reply.")

# def main():
#     logger.info(f"--- 🤖 AI EMAIL BOT STARTED (Checking only LATEST email every {CHECK_INTERVAL}s) ---")
#     logger.info("Press Ctrl+C to stop.")

#     while True:
#         try:
#             # 1. Fetch emails
#             emails = fetch_imap_emails(IMAP_USERNAME, IMAP_PASSWORD, IMAP_SERVER)
            
#             if emails:
#                 # --- CHANGE IS HERE ---
#                 # Get ONLY the single last email (the most recent one)
#                 latest_email = emails[-1] 
                
#                 # Process just that one email
#                 process_single_email(latest_email)
            
#             # 2. Sleep
#             logger.debug(f"Sleeping for {CHECK_INTERVAL} seconds...")
#             time.sleep(CHECK_INTERVAL)

#         except KeyboardInterrupt:
#             logger.info("\nBot stopped by user.")
#             sys.exit(0)
#         except Exception as e:
#             logger.error(f"Critical Error in Main Loop: {e}")
#             logger.info("Restarting loop in 30 seconds...")
#             time.sleep(30)

# if __name__ == "__main__":
#     main()
import os
import sys
from fastapi import FastAPI, HTTPException
from core.email_imap import fetch_imap_emails
from core.email_sender import send_triage_report
from agents.filtering_agent import filter_email
from agents.response_agent import generate_response
from utils.logger import get_logger
from utils.tracker import is_processed, mark_email_as_processed
from config import IMAP_USERNAME, IMAP_PASSWORD, IMAP_SERVER, EMAIL_USERNAME
from dotenv import load_dotenv

# Load Env
load_dotenv()

logger = get_logger(__name__)
app = FastAPI(title="Workday Triage Bot API")

@app.get("/")
def home():
    return {"status": "Online", "usage": "Send a POST request to /run-bot to trigger the agent."}

@app.post("/run-bot")
def trigger_bot_run():
    """
    Endpoint that wakes up the bot, checks Gmail, processes new emails, 
    sends replies, and returns the results.
    """
    logger.info("--- 🚀 API Triggered: Starting Bot Run ---")
    
    results = []
    
    try:
        # 1. Fetch Emails (Same as old code)
        emails = fetch_imap_emails(IMAP_USERNAME, IMAP_PASSWORD, IMAP_SERVER)
        
        if not emails:
            return {"status": "success", "processed_count": 0, "message": "No emails found in Inbox."}

        # Check the last 3 emails
        latest_emails = emails[-3:]
        
        for email in latest_emails:
            email_id = email.get("id")
            subject = email.get("subject", "No Subject")
            sender = email.get("from", "")
            
            # --- Logic from main.py ---
            
            # 1. Deduplication
            if is_processed(email_id):
                continue # Skip silently
            
            # 2. Safety Check
            if EMAIL_USERNAME in sender:
                mark_email_as_processed(email_id)
                continue

            # 3. Filter
            classification = filter_email(email)
            if classification == "spam":
                mark_email_as_processed(email_id)
                results.append({"subject": subject, "status": "Skipped (Spam)"})
                continue

            # 4. Generate Report
            triage_report = generate_response(email)

            # 5. Send Reply
            success = send_triage_report(
                original_subject=subject,
                report_body=triage_report,
                target_email=sender
            )

            if success:
                mark_email_as_processed(email_id)
                results.append({
                    "subject": subject,
                    "sender": sender,
                    "status": "Replied",
                    "classification": classification
                })
            else:
                results.append({"subject": subject, "status": "Failed to Send"})

        logger.info("--- API Run Complete ---")
        return {
            "status": "success",
            "processed_count": len(results),
            "details": results
        }

    except Exception as e:
        logger.error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))