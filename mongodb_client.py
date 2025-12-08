import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://Sheshu:Sheshu123@cluster0.3fpfvmc.mongodb.net/")
DATABASE_NAME = "outlook_webhook"
COLLECTION_NAME = "data"

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        try:
            # Add tlsAllowInvalidCertificates for development (remove in production)
            # For production, use proper SSL certificates
            connection_string = MONGODB_URL
            if "?" not in connection_string:
                connection_string += "?tlsAllowInvalidCertificates=true"
            elif "tlsAllowInvalidCertificates" not in connection_string:
                connection_string += "&tlsAllowInvalidCertificates=true"
            
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {DATABASE_NAME}.{COLLECTION_NAME}")
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            # Don't raise - allow app to continue even if MongoDB fails
            # This way webhook still works even if DB is down
            self.client = None
            self.db = None
            self.collection = None

    def is_message_processed(self, message_id):
        """Check if a message_id has already been processed"""
        if self.collection is None:
            return False
        try:
            # Check if any document exists with this message_id in payload.id
            count = self.collection.count_documents({
                "payload.id": message_id
            })
            return count > 0
        except Exception as e:
            print(f"⚠️ Error checking message_id in MongoDB: {e}")
            return False
    
    def save_webhook_payload(self, payload):
        """Save webhook payload to MongoDB"""
        if self.collection is None:
            print("⚠️ MongoDB not connected, skipping save")
            return None
        try:
            # Check if already exists to prevent duplicates
            message_id = payload.get("id", "")
            if message_id and self.is_message_processed(message_id):
                print(f"⚠️ Message {message_id} already exists in MongoDB, skipping save")
                return None
            
            document = {
                "payload": payload,
                "received_at": datetime.utcnow(),
                "timestamp": datetime.utcnow().isoformat()
            }
            result = self.collection.insert_one(document)
            print(f"✅ Saved webhook payload to MongoDB: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"❌ Error saving to MongoDB: {e}")
            # Don't raise - allow webhook to continue processing
            return None

    def close(self):
        if self.client is not None:
            self.client.close()

# Global instance
mongodb = MongoDBClient()

