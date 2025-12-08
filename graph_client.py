import os
import requests
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

class GraphClient:

    def __init__(self):
        self.token = None

    def get_access_token(self):
        url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

        payload = {
            "client_id": CLIENT_ID,
            "scope": "https://graph.microsoft.com/.default",
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        }

        res = requests.post(url, data=payload)
        
        if res.status_code != 200:
            error_msg = f"Failed to get access token: {res.status_code} - {res.text}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        data = res.json()
        
        if "access_token" not in data:
            error_msg = f"No access token in response: {data}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        self.token = data.get("access_token")
        print(f"✅ Access token obtained successfully")
        return self.token

    def get(self, url):
        if not self.token:
            self.get_access_token()
        headers = {"Authorization": f"Bearer {self.token}"}
        return requests.get(url, headers=headers)

    def post(self, url, payload):
        if not self.token:
            self.get_access_token()
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        
        # If we get 401, token might be expired, try refreshing
        if response.status_code == 401:
            print("🔄 Token expired, refreshing...")
            self.get_access_token()
            headers["Authorization"] = f"Bearer {self.token}"
            response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code not in [200, 201, 202]:
            print(f"❌ POST request failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        return response

    def patch(self, url, payload):
        if not self.token:
            self.get_access_token()
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        return requests.patch(url, json=payload, headers=headers)
    
    def delete(self, url):
        if not self.token:
            self.get_access_token()
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(url, headers=headers)
        
        # If we get 401, token might be expired, try refreshing
        if response.status_code == 401:
            print("🔄 Token expired, refreshing...")
            self.get_access_token()
            headers["Authorization"] = f"Bearer {self.token}"
            response = requests.delete(url, headers=headers)
        
        return response