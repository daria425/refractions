import httpx
import asyncio
import json
from typing import Any, Dict, Union
import os
from dotenv import load_dotenv
from app.logger import logger
from app.image_utils import download_image_from_url, encode_image_to_base64
load_dotenv()
BRIA_API_TOKEN=os.getenv("BRIA_API_TOKEN")


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
            response = await client.post(self.base_url, json=request_payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def create_image_from_text(self, text_prompt: str, **params) -> Dict[str, Any]:
        """
        Submit an image generation request with text prompt and poll until completion.
        Returns the final result when ready.
        """
        request_payload = {"prompt": text_prompt}
        request_payload.update(params)
        request_data = await self.submit_image_gen_request(request_payload)
        request_id = request_data["request_id"]
        return await self.poll_for_status(request_id)
    
    async def create_image_from_structured_prompt(self, structured_prompt: Union[Dict[str, Any], str], **params) -> Dict[str, Any]:
        """
        Submit an image generation request with a structured prompt and poll until completion.
        Returns the final result when ready.
        """
        # API returns/accepts structured_prompt as a JSON string. Allow callers to pass
        # either a dict or a JSON string and normalize to string here.
        if isinstance(structured_prompt, dict):
            sp_string = json.dumps(structured_prompt)
        else:
            sp_string = structured_prompt

        request_payload = {"structured_prompt": sp_string}
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
            "prompt": text_prompt
        }
        request_payload.update(params)
        request_data = await self.submit_image_gen_request(request_payload)
        request_id = request_data["request_id"]
        return await self.poll_for_status(request_id)
    

    async def poll_for_status(self, request_id: str, interval: int = 2, timeout: int = 300) -> Dict[str, Any]:
        """
        Poll for request status until completion or timeout.
        Uses async sleep for non-blocking waits.
        """
        status_url = f"{self.base_url.replace('/image/generate', '/status')}/{request_id}"
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

                if status_state == "COMPLETED":
                    logger.info(f"Request {request_id} completed successfully")
                    url= result.get("image_url")
                    seed= result.get("seed")
                    structured_prompt= result.get("structured_prompt")
                    saved_path=download_image_from_url(url, save_to="file")
                    return {
                        "image_url": url,
                        "seed": seed,
                        "structured_prompt": structured_prompt, 
                        "saved_path": saved_path
                    }

                if asyncio.get_event_loop().time() - start_time > timeout:
                    raise TimeoutError(f"Request {request_id} did not complete within {timeout} seconds")

                await asyncio.sleep(interval)


# Example usage:
async def main():
    url = "https://engine.prod.bria-api.com/v2/image/generate"
    text_prompt="High-quality studio photograph of a modern leather handbag on a marble pedestal, soft diffused lighting, luxury editorial style"

    client = ImageGenClient(
        auth={"api_token": BRIA_API_TOKEN},
        base_url=url
    )
    
    try:
        result_data= await client.create_image_from_text(
            text_prompt,
            model_version="FIBO"
        )
        logger.info(f"Generation completed! Result: {result_data}")
        print(result_data)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise


if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())