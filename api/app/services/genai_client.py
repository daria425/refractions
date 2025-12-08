from google.genai import Client
# from google.auth.credentials import Credentials
from google.oauth2 import service_account
from app.utils.creds import get_vertexai_service_account_info

service_account_info = get_vertexai_service_account_info()
credentials=service_account.Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/cloud-platform"])
google_client = Client(
    vertexai=True, project="social-style-scan", location="us-central1", credentials=credentials
)
