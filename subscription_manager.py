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
    
    def list_subscriptions(self):
        """List all subscriptions."""
        url = "https://graph.microsoft.com/v1.0/subscriptions"
        resp = graph.get(url)
        
        if resp.status_code != 200:
            print(f"❌ Failed to list subscriptions: {resp.status_code}")
            print(f"Response: {resp.text}")
            return {"error": f"Failed to list subscriptions: {resp.status_code}", "subscriptions": []}
        
        data = resp.json()
        subscriptions = data.get("value", [])
        print(f"📋 Found {len(subscriptions)} subscription(s)")
        return {"subscriptions": subscriptions}
    
    def delete_subscription(self, subscription_id):
        """Delete a subscription by ID."""
        url = f"https://graph.microsoft.com/v1.0/subscriptions/{subscription_id}"
        resp = graph.delete(url)
        
        if resp.status_code == 204:
            print(f"✅ Successfully deleted subscription: {subscription_id}")
            return {"status": "success", "subscription_id": subscription_id}
        else:
            print(f"❌ Failed to delete subscription {subscription_id}: {resp.status_code}")
            print(f"Response: {resp.text}")
            return {"status": "error", "subscription_id": subscription_id, "error": resp.text}
    
    def cleanup_duplicate_subscriptions(self):
        """Keep only the latest subscription, delete all others."""
        print("🧹 Cleaning up duplicate subscriptions...")
        
        # Get all subscriptions
        result = self.list_subscriptions()
        subscriptions = result.get("subscriptions", [])
        
        if len(subscriptions) == 0:
            print("ℹ️ No subscriptions found")
            return {"status": "success", "message": "No subscriptions found", "deleted": 0, "kept": 0}
        
        if len(subscriptions) == 1:
            print("ℹ️ Only one subscription exists, nothing to clean up")
            return {"status": "success", "message": "Only one subscription exists", "deleted": 0, "kept": 1}
        
        # Sort by creation time (newest first)
        # Use expirationDateTime as proxy for creation time (newer subscriptions have later expiration)
        subscriptions_sorted = sorted(
            subscriptions,
            key=lambda x: x.get("expirationDateTime", ""),
            reverse=True
        )
        
        # Keep the latest one
        latest = subscriptions_sorted[0]
        latest_id = latest.get("id")
        to_delete = subscriptions_sorted[1:]
        
        print(f"📌 Keeping latest subscription: {latest_id}")
        print(f"🗑️  Deleting {len(to_delete)} duplicate subscription(s)...")
        
        deleted_count = 0
        failed_deletions = []
        
        for sub in to_delete:
            sub_id = sub.get("id")
            print(f"   Deleting subscription: {sub_id}")
            result = self.delete_subscription(sub_id)
            if result.get("status") == "success":
                deleted_count += 1
            else:
                failed_deletions.append(sub_id)
        
        print(f"✅ Cleanup complete: Deleted {deleted_count}/{len(to_delete)} subscription(s)")
        
        if failed_deletions:
            print(f"⚠️  Failed to delete: {failed_deletions}")
        
        return {
            "status": "success",
            "kept": latest_id,
            "deleted": deleted_count,
            "total_found": len(subscriptions),
            "failed_deletions": failed_deletions
        }