import json
import os

from dotenv import load_dotenv


def get_gcs_service_account_info():
    """Load Google service account info from environment variable."""
    load_dotenv()
    api_key_path = os.getenv("STORAGE_SERVICE_ACCOUNT_KEY_PATH")
    if not api_key_path:
        raise ValueError(
            "STORAGE_SERVICE_ACCOUNT_KEY_PATH environment variable is not set."
        )

    with open(api_key_path, "r") as f:
        service_account_info = json.load(f)

    return service_account_info

def get_vertexai_service_account_info():
    """Load Vertex AI service account info from environment variable."""
    load_dotenv()
    api_key_path = os.getenv("VERTEXAI_SERVICE_ACCOUNT_KEY_PATH")
    if not api_key_path:
        raise ValueError(
            "VERTEXAI_SERVICE_ACCOUNT_KEY_PATH environment variable is not set."
        )

    with open(api_key_path, "r") as f:
        service_account_info = json.load(f)

    return service_account_info