from typing import Optional, Literal, Union
from pathlib import Path
import httpx
from datetime import datetime, timezone
import os
import base64
from app.utils.logger import logger
from app.services.storage_service import upload_image_to_gcs
from app.services.genai_client import google_client
from google.genai import types
import io
def download_image_from_url(url: str, save_to: Optional[Literal["file", "gcs"]]="file", dir_name:str="generated_images") -> str:
    """
    Download image content from a given URL.
    Returns the image content as bytes.
    """
    response = httpx.get(url)
    response.raise_for_status()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    file_name=f"generated_image_{ts}.png"
    if save_to=="file":
        os.makedirs(dir_name, exist_ok=True)
        file_path= os.path.join(dir_name, file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)
            logger.info(f"Image saved to {os.path.join(dir_name, file_name)}")
            return file_path
    elif save_to=="gcs":
        gcs_path= f"generated_images/{file_name}"
        gcs_url= upload_image_to_gcs(gcs_path, response.content, content_type="image/png")
        logger.info(f"Image uploaded to GCS at {gcs_url}")
        return gcs_url
    else: 
        raise ValueError("save_to must be either 'file' or 'gcs'")
    


async def encode_image_to_base64(source: Union[str, Path]) -> str:
    """
    Convert image from file path or URL to Base64-encoded string.
    
    Args:
        source: File path (local) or URL (http/https) to the image
        
    Returns:
        Base64-encoded string of the image content
        
    Usage:
        # Local file
        b64 = await encode_image_to_base64("/path/to/image.jpg")
        
        # Remote URL  
        b64 = await encode_image_to_base64("https://example.com/image.jpg")
        
        # Use in JSON payload for agents
        payload = {"image_data": b64, "prompt": "..."}
    """
    source_str = str(source)
    
    try:
        if source_str.startswith(('http://', 'https://')):
            # Download from URL
            logger.info(f"Downloading image from URL: {source_str}")
            async with httpx.AsyncClient() as client:
                response = await client.get(source_str)
                response.raise_for_status()
                image_bytes = response.content
        else:
            # Read from local file
            file_path = Path(source_str)
            if not file_path.exists():
                raise FileNotFoundError(f"Image file not found: {file_path}")
            
            logger.info(f"Reading image from file: {file_path}")
            image_bytes = file_path.read_bytes()
        
        # Encode to Base64
        b64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        logger.info(f"Encoded image to Base64 ({len(image_bytes)} bytes → {len(b64_encoded)} chars)")
        
        return b64_encoded
        
    except Exception as e:
        logger.error(f"Failed to encode image from {source_str}: {e}")
        raise

# TO-DO: refactor to class wheni get bored
def get_image_bytes(image_path: str) -> str:
    """
    Load image bytes from a local file path or URL.
    """
    if image_path.startswith("http://") or image_path.startswith("https://"):
        img_bytes = httpx.get(image_path).content
        return img_bytes
    else:
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
        return img_bytes


def create_image_input(image_bytes: bytes):
    max_bytes = 15 * 1024 * 1024  # 15 MB
    size = len(image_bytes or b"")
    if size > max_bytes:
        image_file = google_client.files.upload(io.BytesIO(image_bytes))
        return image_file
    else:
        image_file = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    return image_file