import json
import os
from utils.logger import get_logger

logger = get_logger(__name__)
TRACKER_FILE = "processed_emails.json"

def load_processed_ids():
    """Loads the list of email IDs that have already been handled."""
    if not os.path.exists(TRACKER_FILE):
        return []
    try:
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def mark_email_as_processed(email_id):
    """Saves an email ID to the file so we don't process it again."""
    processed_ids = load_processed_ids()
    if email_id not in processed_ids:
        processed_ids.append(email_id)
        # Keep file size small: only keep last 1000 IDs
        if len(processed_ids) > 1000:
            processed_ids = processed_ids[-1000:]
            
        with open(TRACKER_FILE, "w") as f:
            json.dump(processed_ids, f)
        logger.debug(f"Marked email {email_id} as processed.")

def is_processed(email_id):
    """Checks if an email ID exists in the tracker."""
    ids = load_processed_ids()
    return email_id in ids