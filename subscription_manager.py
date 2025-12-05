import os
from datetime import datetime, timedelta
from graph_client import GraphClient

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
USER_ID = os.getenv("USER_ID")

graph = GraphClient()

class SubscriptionManager:

    def create_subscription(self):
        expiration = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"

        payload = {
            "changeType": "created",
            "notificationUrl": WEBHOOK_URL,
            "resource": f"/users/{USER_ID}/mailFolders('Inbox')/messages",
            "expirationDateTime": expiration,
            "clientState": "secretCode123"
        }

        resp = graph.post("https://graph.microsoft.com/v1.0/subscriptions", payload)
        return resp.json()

    def renew_subscription(self, subscription_id):
        expiration = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"

        payload = {
            "expirationDateTime": expiration
        }

        url = f"https://graph.microsoft.com/v1.0/subscriptions/{subscription_id}"
        resp = graph.patch(url, payload)
        return resp.json()
