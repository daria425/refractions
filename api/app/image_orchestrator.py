
from app.image_gen_client import ImageGenClient, get_image_gen_client
from app.utils.image_utils import get_image_bytes
from app.utils.logger import logger
from app.agent import translate_vision_to_image_prompt
from app.db.db_collections import ImagesCollection
import json
import asyncio  # CHANGE: use asyncio primitives for non-blocking waits and concurrency
from typing import Any, Dict, List  # CHANGE: add typing for clearer contracts and results
class ImageGenOrchestrator:
    def __init__(self, vision: str, image_path: str, ):
        self.image_path = image_path
        self.vision = vision
        self.prompts={}
        self.image_bytes=None

    async def generate_one(
        self,
        shot_type: str,
        item: Dict[str, str],
        image_gen_client: ImageGenClient,
        images_collection: ImagesCollection,
        semaphore: asyncio.Semaphore,
        wait_time: int,
        per_request_timeout: int,
    ) -> Dict[str, Any]:
        """
        Generate a single shot. Do not raise; return an error dict so the batch continues.
        Exception isolation lives here to avoid cancelling sibling tasks.  # CHANGE
        """
        text_prompt = item.get("prompt", "")
        reasoning = item.get("reasoning", "")

        if not text_prompt:
            logger.error(f"Skipping shot '{shot_type}': empty prompt")  # CHANGE: soft-fail invalid input
            return {
                "shot_type": shot_type,
                "status": "error",
                "error": {"type": "input_error", "message": "empty prompt"},
            }

        logger.info(
            f"Generating image for {shot_type} with prompt (len={len(text_prompt)}): {text_prompt[:200]}"
        )

        async with semaphore:
            try:
                # CHANGE: Bound the request to prevent hanging workers
                result_data = await asyncio.wait_for(
                    image_gen_client.create_image_from_text(
                        text_prompt=text_prompt,
                        model_version="FIBO",
                    ),
                    timeout=per_request_timeout,
                )

                if isinstance(result_data, dict) and "error" in result_data:
                    logger.error(f"Client returned error for {shot_type}: {result_data['error']}")
                    return {"shot_type": shot_type, "status": "error", "error": result_data["error"]}

                sp_field = result_data.get("structured_prompt")
                if isinstance(sp_field, str):
                    try:
                        result_data["structured_prompt"] = json.loads(sp_field)
                    except json.JSONDecodeError:
                        logger.warning(
                            f"structured_prompt not valid JSON for {shot_type}; leaving as string"
                        )  # CHANGE

                logger.info(f"Generation completed for {shot_type}")

                saved_data = {
                    "metadata": result_data,
                    "text_prompt": text_prompt,
                    "reasoning": reasoning,
                    "shot_type": shot_type,
                }

                try:
                    images_collection.insert_data(saved_data)  # CHANGE: isolate DB failures per shot
                except Exception as db_err:
                    logger.error(f"DB insert failed for {shot_type}: {db_err}")
                    return {
                        "shot_type": shot_type,
                        "status": "error",
                        "error": {"type": "db_error", "message": str(db_err)},
                    }

                if wait_time:
                    await asyncio.sleep(wait_time)  # optional pacing
                return {"shot_type": shot_type, "status": "ok", "data": result_data}

            except asyncio.TimeoutError:
                logger.error(f"Timeout for {shot_type}: exceeded {per_request_timeout}s")  # CHANGE
                return {
                    "shot_type": shot_type,
                    "status": "error",
                    "error": {"type": "timeout", "message": f"did not complete within {per_request_timeout}s"},
                }
            except Exception as e:
                logger.error(f"Unhandled error for {shot_type}: {e}")
                return {
                    "shot_type": shot_type,
                    "status": "error",
                    "error": {"type": "unhandled", "message": str(e)},
                }

    def setup(self):
        self.image_bytes= get_image_bytes(self.image_path)
        logger.info(f"Loaded image bytes from {self.image_path}")


    def get_prompts(self):
        prompts = translate_vision_to_image_prompt(self.vision, self.image_bytes)
        self.prompts = prompts.response.model_dump()
        if not isinstance(self.prompts, dict) or not self.prompts:
            logger.error("No prompts returned from translation step; skipping generation") 
            self.prompts = {}

    async def generate_images(
        self,
        image_gen_client: ImageGenClient,
        images_collection: ImagesCollection,
        wait_time: int,
        max_concurrency: int = 4, 
        per_request_timeout: int = 120, 
    ) -> List[Dict[str, Any]]:
        """Generate images for all prompts with concurrency.

        Per-shot failures return structured error dicts; tasks do not raise, so the batch completes.  # CHANGE
        """
        semaphore = asyncio.Semaphore(max_concurrency)
        tasks: List[asyncio.Task] = [
            asyncio.create_task(
                self.generate_one(
                    shot_type=k,
                    item=v,
                    image_gen_client=image_gen_client,
                    images_collection=images_collection,
                    semaphore=semaphore,
                    wait_time=wait_time,
                    per_request_timeout=per_request_timeout,
                )
            )
            for k, v in self.prompts.items()
        ]

        return await asyncio.gather(*tasks)  # CHANGE: tasks return dicts; no exceptions bubble here

    async def run(
        self,
        image_gen_client: ImageGenClient,
        images_collection: ImagesCollection,
        wait_time: int = 0, 
        max_concurrency: int = 4, 
        per_request_timeout: int = 120, 
    ) -> List[Dict[str, Any]]:
        self.setup()
        self.get_prompts()
        return await self.generate_images(
            image_gen_client,
            images_collection,
            wait_time,
            max_concurrency=max_concurrency,
            per_request_timeout=per_request_timeout,
        )


# Example usage:
async def main():
    from app.db.db_connection import DatabaseConnection
    from app.db.db_collections import ImagesCollection
    db= DatabaseConnection.get_instance()
    db.initialize_mongo_client()
    images_collection= ImagesCollection()
    image_gen_client=get_image_gen_client()
    image_path="./input_images/tech_drawing_sample.png"
    vision="Oriental maximalism, vibrant, gold accents, intricate patterns"
    orchestrator= ImageGenOrchestrator(vision, image_path)
    result= await orchestrator.run(
        image_gen_client=image_gen_client,
        images_collection=images_collection)
    return result

if __name__ == "__main__":
    res=asyncio.run(main())
    print(res)


    


