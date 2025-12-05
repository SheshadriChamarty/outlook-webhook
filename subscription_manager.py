import os
from datetime import datetime, timedelta
from graph_client import GraphClient

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
USER_ID = os.getenv("USER_ID")

graph = GraphClient()

class SubscriptionManager:

    def create_subscription(self):
        # Validate environment variables
        if not WEBHOOK_URL:
            return {"error": "WEBHOOK_URL environment variable is not set"}
        if not USER_ID:
            return {"error": "USER_ID environment variable is not set"}
        
        expiration = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"

        payload = {
            "changeType": "created",
            "notificationUrl": WEBHOOK_URL,
            "resource": f"/users/{USER_ID}/mailFolders('Inbox')/messages",
            "expirationDateTime": expiration,
            "clientState": "secretCode123"
        }

        print(f"📤 Creating subscription for user: {USER_ID}")
        print(f"📤 Webhook URL: {WEBHOOK_URL}")
        print(f"📤 Payload: {payload}")

        resp = graph.post("https://graph.microsoft.com/v1.0/subscriptions", payload)
        
        print(f"📥 Response status: {resp.status_code}")
        print(f"📥 Response body: {resp.text}")
        
        return resp.json()

    def renew_subscription(self, subscription_id):
        expiration = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"

        payload = {
            "expirationDateTime": expiration
        }

        url = f"https://graph.microsoft.com/v1.0/subscriptions/{subscription_id}"
        resp = graph.patch(url, payload)
        return resp.json()
