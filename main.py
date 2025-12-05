from fastapi import FastAPI, Request, Response
from subscription_manager import SubscriptionManager
from email_processor import fetch_email, process_email
import os
import json

USER_ID = os.getenv("USER_ID")

app = FastAPI()
subscriptions = SubscriptionManager()

@app.get("/")
def root():
    return {"message": "Outlook Webhook Running"}

# Endpoint to manually create subscription
@app.post("/create-subscription")
def create():
    return subscriptions.create_subscription()

# Endpoint MS Graph calls for validation + notifications
@app.api_route("/email-webhook", methods=["GET", "POST"])
async def email_webhook(request: Request):
    # 🔹 STEP 1: VALIDATION REQUEST
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        return Response(content=validation_token, media_type="text/plain")

    # 🔹 STEP 2: NOTIFICATION EVENT
    body = await request.body()
    data = json.loads(body.decode("utf-8"))

    for record in data.get("value", []):
        message_id = record["resourceData"]["id"]

        # Fetch complete email
        print("📩 Fetching email:", message_id)
        email_json = fetch_email(message_id, USER_ID)

        # Process it
        process_email(email_json)

    return {"status": "success"}

