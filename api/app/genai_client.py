from google.genai import Client

google_client = Client(
    vertexai=True, project="social-style-scan", location="us-central1"
)
