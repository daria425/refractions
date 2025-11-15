from typing import Optional, Literal
import httpx
from datetime import datetime, timezone
import os
from app.logger import logger
from app.storage_service import upload_image_to_gcs
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



