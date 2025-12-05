# core/email_imap.py
import imaplib
import email
from email.header import decode_header

def fetch_imap_emails(username, password, imap_server="imap.gmail.com"):
    print(f"Connecting to {imap_server}...")
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        mail.select("inbox")
        
        # Search for all emails
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        # --- CRITICAL FIX START ---
        # Only take the last 5 emails to prevent freezing
        print(f"Total emails in inbox: {len(email_ids)}. Fetching the last 5...")
        latest_email_ids = email_ids[-5:] 
        # --- CRITICAL FIX END ---
        
        emails = []
        for num in latest_email_ids:
            try:
                # Fetch the email content
                status, msg_data = mail.fetch(num, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Decode Subject safely
                subject_header = msg.get("Subject")
                if subject_header:
                    decoded_list = decode_header(subject_header)
                    subject, encoding = decoded_list[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                else:
                    subject = "(No Subject)"

                emails.append({
                    "id": num.decode(),
                    "from": msg.get("From"),
                    "subject": subject,
                    "body": extract_email_body(msg)
                })
            except Exception as e:
                print(f"Skipping email ID {num}: {e}")
                continue
                
        mail.logout()
        return emails
    except Exception as e:
        print(f"IMAP Connection Error: {e}")
        return []

def extract_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                charset = part.get_content_charset() or "utf-8"
                try:
                    return part.get_payload(decode=True).decode(charset, errors="replace")
                except:
                    return ""
    else:
        charset = msg.get_content_charset() or "utf-8"
        try:
            return msg.get_payload(decode=True).decode(charset, errors="replace")
        except:
            return ""
    return ""