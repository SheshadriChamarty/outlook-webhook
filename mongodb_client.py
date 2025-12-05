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

    def save_webhook_payload(self, payload):
        """Save webhook payload to MongoDB"""
        if not self.collection:
            print("⚠️ MongoDB not connected, skipping save")
            return None
        try:
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
        if self.client:
            self.client.close()

# Global instance
mongodb = MongoDBClient()

