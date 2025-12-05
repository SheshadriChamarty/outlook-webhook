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
        data = res.json()
        self.token = data.get("access_token")
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
        return requests.post(url, json=payload, headers=headers)

    def patch(self, url, payload):
        if not self.token:
            self.get_access_token()
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        return requests.patch(url, json=payload, headers=headers)
