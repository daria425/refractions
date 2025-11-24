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
import trimesh
import numpy as np
from PIL import Image
from pygltflib import GLTF2
def patch_glb_transparency(glb_path: str, alpha_mode: str = "BLEND", double_sided: bool = True, alpha_cutoff: float = 0.5) -> None:
    """
    # CHANGE: Ensure PNG transparency works in viewers (e.g., MS 3D Viewer)
    Sets material alphaMode and doubleSided on the exported GLB.
    Safe no-op if pygltflib is not available or file cannot be patched.
    """
    if GLTF2 is None:
        logger.warn("pygltflib not installed; skipping GLB transparency patch")
        return
    try:
        glb = GLTF2().load(glb_path)
        if glb.materials:
            for m in glb.materials:
                # alphaMode: OPAQUE | MASK | BLEND
                m.alphaMode = alpha_mode
                m.doubleSided = double_sided
                if alpha_mode == "MASK":
                    # default 0.5 if not set
                    m.alphaCutoff = alpha_cutoff
        glb.save(glb_path)
        logger.info(f"Patched GLB transparency (alphaMode={alpha_mode}, doubleSided={double_sided}) for {glb_path}")
    except Exception as e:
        logger.error(f"Failed to patch GLB transparency for {glb_path}: {e}")

def image_to_glb_plane(image_path: str, glb_out: str = "image_plane.glb", height: float = 1.0, flip_v: bool = True):
    """Export a textured plane GLB for a single image.

    Args:
        image_path: Source image (PNG with transparency recommended).
        glb_out: Output GLB path.
        height: Desired plane height in world units.
        flip_v: Flip the V (vertical) UV coordinate to correct upside-down textures in viewers.  # CHANGE
    """
    img = Image.open(image_path).convert("RGBA")  # CHANGE: ensure RGBA for transparency
    w, h = img.size
    aspect = w / h
    half_h = height / 2
    half_w = aspect * half_h
    vertices = np.array([
        [-half_w, -half_h, 0.0],
        [ half_w, -half_h, 0.0],
        [ half_w,  half_h, 0.0],
        [-half_w,  half_h, 0.0],
    ])
    faces = np.array([[0,1,2],[0,2,3]])

    # CHANGE: Conditionally flip V coordinate so texture appears correctly oriented in glTF viewers
    if flip_v:
        uv = np.array([
            [0.0, 0.0],  # bottom-left
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
        ])
    else:
        uv = np.array([
            [0.0, 1.0],  # original mapping (may look upside down depending on viewer)
            [1.0, 1.0],
            [1.0, 0.0],
            [0.0, 0.0],
        ])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.visual = trimesh.visual.texture.TextureVisuals(uv=uv, image=img)
    scene = trimesh.Scene(mesh)
    scene.export(glb_out)  # writes a self-contained .glb
    # CHANGE: Patch GLB so transparency shows up in common viewers (e.g., MS 3D Viewer)
    patch_glb_transparency(glb_out, alpha_mode="BLEND", double_sided=True)
    return glb_out

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
def get_image_bytes(image_data: Union[str, bytes]) -> str:
    """
    Load image bytes from a local file path or URL.
    """
    if isinstance(image_data, bytes):
        return image_data
    if image_data.startswith("http://") or image_data.startswith("https://"):
        img_bytes = httpx.get(image_data).content
        return img_bytes
    else:
        with open(image_data, "rb") as img_file:
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

if __name__ == "__main__":
    image_path="./input_images/dress.png"
    out_path=image_to_glb_plane(image_path, glb_out="image_plane.glb", height=1.0)
    print(f"Exported GLB to {out_path}")
