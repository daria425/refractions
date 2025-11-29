import httpx
import asyncio
import json
from typing import Any, Dict, Union, Optional
from functools import lru_cache
import os
from dotenv import load_dotenv
from app.utils.logger import logger
from app.utils.image_utils import download_image_from_url, encode_image_to_base64
load_dotenv()
BRIA_API_TOKEN=os.getenv("BRIA_API_TOKEN")
DEFAULT_BASE_URL="https://engine.prod.bria-api.com/v2"

class ImageGenClient:
    def __init__(self, auth: Dict, base_url: str):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            **auth
        }

    async def submit_image_gen_request(self, request_payload:Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an image. Additional optional parameters can be passed via kwargs
        and will be merged into the JSON payload sent to the API.
        Example: await client.submit_image_gen_request("...", model_version="FIBO", width=1024, height=1024)
        """
        logger.info(f"Submitting image generation request to {self.base_url} with payload keys: {list(request_payload.keys())}")
        async with httpx.AsyncClient() as client:
            image_gen_url=f"{self.base_url}/image/generate"
            response = await client.post(image_gen_url, json=request_payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def create_image_from_text(self, text_prompt: str, **params) -> Dict[str, Any]:
        """
        Submit an image generation request with text prompt and poll until completion.
        Returns the final result when ready.
        """
        request_payload = {"prompt": text_prompt, 
                            "visual_output_content_moderation": False}
        request_payload.update(params)
        request_data = await self.submit_image_gen_request(request_payload)
        request_id = request_data["request_id"]
        return await self.poll_for_status(request_id)
    
    async def create_image_from_structured_prompt(self, structured_prompt: Union[Dict[str, Any], str], **params) -> Dict[str, Any]:
        """
        Submit an image generation request with a structured prompt and poll until completion.
        Returns the final result when ready.
        """
        if isinstance(structured_prompt, dict):
            sp_string = json.dumps(structured_prompt)
        else:
            sp_string = structured_prompt

        request_payload = {"structured_prompt": sp_string,
                                       "visual_output_content_moderation": False}
        request_payload.update(params)
        request_data = await self.submit_image_gen_request(request_payload)
        request_id = request_data["request_id"]
        return await self.poll_for_status(request_id)
    
    async def create_image_from_image(self, image_url: str, **params) -> Dict[str, Any]:
        """
        Submit an image generation request with an image URL and poll until completion.
        Returns the final result when ready.
        """
        image_data= await encode_image_to_base64(image_url)
        request_payload = {"images": [image_data]}
        request_payload.update(params)
        request_data = await self.submit_image_gen_request(request_payload)
        request_id = request_data["request_id"]
        return await self.poll_for_status(request_id)
    
    async def create_image_from_image_and_text(self, image_url: str, text_prompt: str, **params) -> Dict[str, Any]:
        """
        Submit an image generation request with an image URL and text prompt, then poll until completion.
        Returns the final result when ready.
        """
        image_data= await encode_image_to_base64(image_url)
        request_payload = {
            "images": [image_data],
            "prompt": text_prompt,
            "visual_output_content_moderation": False
        }
        request_payload.update(params)
        request_data = await self.submit_image_gen_request(request_payload)
        request_id = request_data["request_id"]
        return await self.poll_for_status(request_id)
    
    async def refine_prev_image(self, seed:int, structured_prompt:Dict[str, Any], new_prompt:str, **params):
        if isinstance(structured_prompt, dict):
            sp_string = json.dumps(structured_prompt)
        else:
            sp_string = structured_prompt
        request_payload = {"structured_prompt": sp_string,
                           "visual_output_content_moderation": False, 
                           "seed": seed, 
                           "prompt": new_prompt
                           }
        request_payload.update(params)
        request_data = await self.submit_image_gen_request(request_payload)
        request_id = request_data["request_id"]
        return await self.poll_for_status(request_id)



    async def poll_for_status(self, request_id: str, interval: int = 2, timeout: int = 300) -> Dict[str, Any]:
        """
        Poll for request status until completion or timeout.
        Uses async sleep for non-blocking waits.
        RETURNS:
          - Success dict: {"image_url", "seed", "structured_prompt", "saved_path", "request_id"}
          - Error dict: {"error": {"type": str, "message": str, "request_id": str, "status": str}}
        RATIONALE: Return error structures instead of raising so orchestrators can decide per-shot behavior.  # CHANGE: switch from raise to error dict
        """
        status_url = f"{self.base_url}/status/{request_id}"
        logger.info(f"Polling status URL: {status_url}")

        start_time = asyncio.get_event_loop().time()

        async with httpx.AsyncClient() as client:
            while True:
                status_response = await client.get(status_url, headers=self.headers)
                status_response.raise_for_status()
                status_data = status_response.json()
                status_state = status_data.get("status")
                result = status_data.get("result")
                logger.info(f"Request {request_id} is {status_state}.")

                if status_state == "ERROR":
                    # Extract any error details returned by the API
                    error_detail = status_data.get("error")
                    logger.error(f"Request {request_id} failed with error: {error_detail}")
                    return {  # CHANGE: return structured error instead of raising to keep batch resilient
                        "error": {
                            "type": "api_error",
                            "message": str(error_detail) if error_detail else "unknown error",
                            "request_id": request_id,
                            "status": "ERROR",
                        }
                    }

                if status_state == "COMPLETED":
                    logger.info(f"Request {request_id} completed successfully")
                    url = result.get("image_url")
                    seed = result.get("seed")
                    structured_prompt = result.get("structured_prompt")
                    saved_path = download_image_from_url(url, save_to="gcs")  
                    return {
                        "image_url": url,
                        "seed": seed,
                        "structured_prompt": structured_prompt,
                        "saved_path": saved_path,
                        "request_id": request_id,
                        "status": "SUCCESS"
                    }

                if asyncio.get_event_loop().time() - start_time > timeout:
                    logger.error(f"Request {request_id} timed out after {timeout}s")
                    return {
                        "error": {
                            "type": "timeout",
                            "message": f"did not complete within {timeout} seconds",
                            "request_id": request_id,
                            "status": "TIMEOUT",
                        }
                    }
                await asyncio.sleep(interval)

@lru_cache(maxsize=1)
def get_image_gen_client(auth:Dict[str, str]={"api_token": BRIA_API_TOKEN}, base_url: str = DEFAULT_BASE_URL) -> ImageGenClient:
    return ImageGenClient(auth=auth, base_url=base_url)

if __name__ == "__main__":
    # Simple test of the client w structured prompt
    async def test():
        client = get_image_gen_client()
        structured_prompt={
  "aesthetics": {
    "aesthetic_score": "very high",
    "color_scheme": "Monochromatic and analogous, dominated by soft neutrals (dusty taupe, light stone, off-white) with subtle accents of black and white from the dress pattern and muted pastels from the background blossoms. The overall palette is serene and sophisticated.",
    "composition": "Full-length portrait composition, with the model centered and filling the frame vertically, adhering to a 4:5 aspect ratio. The lines of the dress and the model's posture create leading lines that draw the eye upwards.",
    "mood_atmosphere": "Elegant, serene, sophisticated, and subtly artistic with a touch of ethereal beauty.",
    "preference_score": "very high"
  },
  "artistic_style": "realistic",
  "background_setting": "A minimalist studio environment with a simple, textured wall behind the model. The wall is a neutral, light gray or off-white, providing a clean backdrop that allows the dress and model to stand out. Large, soft-focus spring blossoms are subtly integrated into the background, appearing as ethereal blurs of pastel color, suggesting depth and a touch of organic beauty without distracting from the main subject.",
  "context": "This is a concept for a high-fashion editorial photograph, potentially for a luxury fashion magazine or a designer's lookbook, emphasizing the garment's unique design and artistic elements.",
  "lighting": {
    "conditions": "Soft, diffused morning light",
    "direction": "Front-lit, with a gentle glow from the upper-left, mimicking natural window light.",
    "shadows": "Very soft, subtle shadows, particularly around the model's form and the drapes of the dress, adding dimension without harshness. The background blossoms cast almost imperceptible, extremely soft shadows."
  },
  "objects": [
    {
      "action": "Standing poised, subtly modeling the dress.",
      "appearance_details": "Long, flowing dark brown hair styled naturally, framing her face. Minimal, natural-looking makeup highlighting her features.",
      "clothing": "An asymmetrical, full-length dress in dusty taupe and light stone. It features a single-shoulder drape on her left side, strategic waist cut-outs, and panels embellished with an intricate black and white surreal floral line-art pattern. The fabric appears to have a soft, flowing quality.",
      "description": "A tall, slender female model, embodying elegance and poise, showcasing the intricate details of the dress. Her posture is graceful yet commanding, drawing the viewer's eye to the garment.",
      "expression": "Serene and confident, with a subtle, knowing gaze directed slightly off-camera.",
      "gender": "female",
      "location": "center",
      "orientation": "Facing slightly to her right, body turned three-quarters towards the viewer.",
      "pose": "Standing gracefully, with her left arm slightly bent at the elbow and her hand gently resting on her left hip, and her right arm extended downwards, subtly showcasing the dress's drape. Her weight is shifted slightly to her right leg.",
      "relationship": "The primary subject, interacting directly with the dress and contrasting subtly with the soft background.",
      "relative_size": "large within frame",
      "shape_and_color": "Slender human form, warm skin tones.",
      "skin_tone_and_texture": "Medium-toned, smooth skin with a healthy glow.",
      "texture": "Smooth, radiant skin."
    },
    {
      "appearance_details": "The line-art pattern features abstract, intertwined floral motifs that appear hand-drawn, creating a dynamic contrast with the solid color blocks. The waist cut-outs are clean and architectural.",
      "description": "The asymmetrical dress is the focal point of the fashion shoot, designed with a sophisticated blend of dusty taupe and light stone colors. Its unique structure includes a single-shoulder drape that cascades elegantly over her left shoulder, precise waist cut-outs that add a modern edge, and distinct panels. These panels are adorned with an intricate, surreal floral line-art pattern in stark black and white, adding a captivating artistic element to the garment.",
      "location": "center",
      "orientation": "Draped and flowing according to the model's pose.",
      "relationship": "Worn by the model, it is the primary subject of the photograph.",
      "relative_size": "large within frame",
      "shape_and_color": "Flowing, asymmetrical silhouette in dusty taupe, light stone, and black and white.",
      "texture": "Smooth, possibly silk or a similar fine fabric, with a soft sheen."
    }
  ],
  "photographic_characteristics": {
    "camera_angle": "Eye-level, providing a direct and engaging view of the model.",
    "depth_of_field": "Shallow, with the model and dress in sharp focus and the background blossoms rendered in a soft, dreamy bokeh.",
    "focus": "Sharp focus on the model and the intricate details of the dress.",
    "lens_focal_length": "Portrait lens (e.g., 85mm-100mm) to achieve a flattering perspective and good subject isolation."
  },
  "short_description": "A full-length fashion photograph captures a female model in an asymmetrical dress featuring dusty taupe and light stone colors, a single-shoulder drape, waist cut-outs, and panels adorned with intricate black and white surreal floral line-art. She stands elegantly in a minimalist studio, bathed in soft, diffused morning light, against a textured wall with large, soft-focus spring blossoms, creating a serene and sophisticated visual.",
  "style_medium": "photograph"
}
        result = await client.create_image_from_structured_prompt(
            structured_prompt=structured_prompt,
            model_version="FIBO",
            # width=1024,
            # height=1024
        )
        print(result)
    
    asyncio.run(test())