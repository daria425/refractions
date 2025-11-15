from datetime import timedelta

from google.cloud import storage

from app.utils.creds import get_google_service_account_info

service_account_info = get_google_service_account_info()
storage_client = storage.Client.from_service_account_info(service_account_info)


def upload_image_to_gcs(
    destination_blob_name: str, image_bytes: bytes, content_type: str = "image/png"
) -> str:
    """
    Uploads image bytes to GCS and returns a dict with bucket and blob info for MongoDB.
    """
    bucket_name = "refractions"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(image_bytes, content_type=content_type)
    url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
    return url
