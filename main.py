from fastapi import FastAPI, Request, Response, BackgroundTasks
from subscription_manager import SubscriptionManager
from email_processor import fetch_email, process_email
from mongodb_client import mongodb
import os
import json
from dotenv import load_dotenv

load_dotenv()

USER_ID = os.getenv("USER_ID")

app = FastAPI()
subscriptions = SubscriptionManager()

def process_email_async(message_id: str):
    """Process email asynchronously in background"""
    try:
        # Check again (race condition protection)
        if mongodb.is_message_processed(message_id):
            print(f"⏭️  Message {message_id} already processed (race condition check)")
            return
        
        # Fetch complete email
        print(f"📩 Fetching email: {message_id}")
        email_json = fetch_email(message_id, USER_ID)

        # Save email_json to MongoDB (this also checks for duplicates)
        print("💾 Saving email to MongoDB...")
        try:
            mongodb.save_webhook_payload(email_json)
        except Exception as db_error:
            print(f"⚠️ MongoDB save error (continuing anyway): {db_error}")

        # Process it
        process_email(email_json)
    except Exception as e:
        print(f"❌ Error processing email {message_id} in background: {e}")

@app.get("/")
def root():
    return {"message": "Outlook Webhook Running"}

# Endpoint to check token and permissions
@app.get("/check-token")
def check_token():
    from graph_client import GraphClient
    graph = GraphClient()
    try:
        token = graph.get_access_token()
        # Decode token to see scopes (basic check)
        import base64
        parts = token.split('.')
        if len(parts) >= 2:
            # Add padding if needed
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            import json
            token_data = json.loads(decoded)
            return {
                "status": "Token obtained",
                "scopes": token_data.get("roles", []),
                "app_id": token_data.get("appid"),
                "note": "Check that 'Subscription.ReadWrite.All' and 'Mail.Read' are in the roles list"
            }
    except Exception as e:
        return {"error": str(e)}

# Endpoint to manually create subscription
@app.post("/create-subscription")
def create():
    return subscriptions.create_subscription()

# Endpoint to list all subscriptions
@app.get("/list-subscriptions")
def list_subs():
    return subscriptions.list_subscriptions()

# Endpoint to cleanup duplicate subscriptions (keep only latest)
@app.post("/cleanup-subscriptions")
def cleanup_subs():
    return subscriptions.cleanup_duplicate_subscriptions()

# Endpoint MS Graph calls for validation + notifications
@app.api_route("/email-webhook", methods=["GET", "POST"])
async def email_webhook(request: Request, background_tasks: BackgroundTasks):
    # 🔹 STEP 1: VALIDATION REQUEST
    # Microsoft Graph sends GET request with validationToken query parameter
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        # Must return 200 OK with validation token as plain text
        return Response(
            content=validation_token,
            media_type="text/plain",
            status_code=200
        )

    # 🔹 STEP 2: NOTIFICATION EVENT
    if request.method == "POST":
        try:
            body = await request.body()
            if not body:
                return Response(content="Empty body", status_code=400)
            
            data = json.loads(body.decode("utf-8"))
            
            # Extract message IDs for background processing
            message_ids = []
            for record in data.get("value", []):
                message_id = record["resourceData"]["id"]
                
                # Quick deduplication check before adding to background tasks
                if mongodb.is_message_processed(message_id):
                    print(f"⏭️  Message {message_id} already processed, skipping to prevent duplicates")
                    continue
                
                message_ids.append(message_id)
            
            # If no new messages, return immediately
            if not message_ids:
                return {"status": "success", "message": "All messages already processed"}
            
            # Add emails to background processing queue
            for message_id in message_ids:
                background_tasks.add_task(process_email_async, message_id)
            
            # Return immediately (within ~100ms) - Graph API will not retry
            # Background tasks will process emails asynchronously
            return {"status": "accepted", "message_ids": message_ids, "message": "Processing in background"}
        except json.JSONDecodeError:
            return Response(content="Invalid JSON", status_code=400)
        except Exception as e:
            print(f"Error processing notification: {e}")
            return Response(content=f"Error: {str(e)}", status_code=500)
    
    # If GET request without validationToken, return 400
    return Response(content="Missing validationToken", status_code=400)

