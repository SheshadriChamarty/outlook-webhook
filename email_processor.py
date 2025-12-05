from graph_client import GraphClient

graph = GraphClient()

def fetch_email(message_id, user_id):
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{message_id}"
    response = graph.get(url)
    return response.json()

def process_email(email_json):
    subject = email_json.get("subject", "No subject")
    body = email_json.get("body", {}).get("content", "")
    sender = email_json.get("from", {}).get("emailAddress", {}).get("address")

    print("🔥 New Email Received")
    print("From:", sender)
    print("Subject:", subject)
    print("Body:", body)

    # 👉 Your custom logic goes here
    # send to your API
    # extract OTP
    # store in DB
    # trigger workflow

    return {"status": "processed", "subject": subject}
