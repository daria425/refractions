import httpx
import asyncio
import json
from typing import Any, Dict, Union
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
                    saved_path = download_image_from_url(url, save_to="file")  # TO-DO: sync I/O; can offload if needed
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
# Example usage:
# async def main():
#     from app.utils.image_utils import get_image_bytes
#     from app.agent import translate_vision_to_image_prompt
#     from app.db.db_connection import DatabaseConnection
#     from app.db.db_collections import ImagesCollection
#     import json
#     db= DatabaseConnection.get_instance()
#     db.initialize_mongo_client()
#     images_collection= ImagesCollection()
#     import time
#     url = "https://engine.prod.bria-api.com/v2/image/generate"
#     client = ImageGenClient(
#         auth={"api_token": BRIA_API_TOKEN},
#         base_url=url
#     )
#     image_path="./input_images/tech_drawing_sample.png"
#     vision="Minimal luxury"
#     image_bytes= get_image_bytes(image_path)
#     prompts= translate_vision_to_image_prompt(vision, image_bytes)
#     processed_prompts=prompts.response.model_dump()

#     for k, v in processed_prompts.items():
#         text_prompt=v["prompt"]
#         reasoning=v["reasoning"]
#         logger.info(f"Generating image for {k} with prompt: {text_prompt}")
#         try:
#             result_data= await client.create_image_from_text(
#                 text_prompt=text_prompt,
#                 model_version="FIBO"
#             )
#             if isinstance(result_data, dict) and "error" in result_data:
#                 # CHANGE: handle error return without raising to allow loop to continue
#                 logger.error(f"Generation error for {k}: {result_data['error']}")
#                 continue
#             sp_dict=json.loads(result_data.get("structured_prompt", "{}"))
#             result_data["structured_prompt"]=sp_dict
#             logger.info(f"Generation completed! Result: {result_data}")
#             saved_data={
#                "metadata": result_data,
#                "text_prompt": text_prompt,
#                 "reasoning": reasoning, 
#                 "shot_type": k
#             }
#             images_collection.insert_data(saved_data)
#             await asyncio.sleep(2)  # CHANGE: avoid blocking the event loop in async context
#         except Exception as e:
#             logger.error(f"Generation failed: {e}")
#             raise


# if __name__ == "__main__":
#     # Run the async example
#     asyncio.run(main())