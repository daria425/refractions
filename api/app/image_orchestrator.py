from app.image_gen_client import ImageGenClient, get_image_gen_client
from app.utils.image_utils import get_image_bytes
from app.utils.logger import logger
from app.agent import translate_vision_to_image_prompt
from app.db.db_collections import GeneratedImagesCollection
import json
import asyncio 
from typing import Any, Dict, List, Literal, Optional, Union, Callable, Awaitable


class ImageGenOrchestrator:
    def __init__(self, vision: Optional[str] = None, uploaded_image: Optional[Union[str, bytes]] = None):
        self.uploaded_image = uploaded_image
        self.vision = vision
        self.prompts: Dict[str, Any] = {}
        self.image_bytes: Optional[bytes] = None
        self.variants: Dict[str, Any] = {}

    # ========= Variants / Refinement =========
    async def refine_one(
        self,
        seed: str,  # prev image seed
        structured_prompt: Dict[str, Any],  # prev structured prompt
        request_id: str,
        variant_item: Dict[str, str],
        image_gen_client: ImageGenClient,
        images_collection: GeneratedImagesCollection,
        semaphore: asyncio.Semaphore,
        wait_time: int,
        per_request_timeout: int,
    ) -> Dict[str, Any]:
        new_prompt = variant_item.get("description")
        label = variant_item.get("variant_label", "unknown_variant")
        logger.info(f"Refining image for variant '{label}' with prompt: {new_prompt[:200]}")
        async with semaphore:
            try:
                refined_result = await asyncio.wait_for(
                    image_gen_client.refine_prev_image(
                        seed=seed, structured_prompt=structured_prompt, new_prompt=new_prompt
                    ),
                    timeout=per_request_timeout,
                )

                if isinstance(refined_result, dict) and "error" in refined_result:
                    logger.error(f"Client returned error for {label}: {refined_result['error']}")
                    return {"label": label, "status": "error", "error": refined_result["error"]}

                sp_field = refined_result.get("structured_prompt")
                if isinstance(sp_field, str):
                    try:
                        refined_result["structured_prompt"] = json.loads(sp_field)
                    except json.JSONDecodeError:
                        logger.warning(f"structured_prompt not valid JSON for {label}; leaving as string")

                logger.info(f"Generation completed for {label}")

                saved_data = {
                    "variant_label": label,
                    "refinement_data": {
                        "previous_seed": seed,
                        "previous_structured_prompt": structured_prompt,
                        "new_prompt": new_prompt,
                    },
                    "result_data": refined_result,
                }

                try:
                    images_collection.update_image_with_variant(request_id, saved_data)
                except Exception as db_err:
                    logger.error(f"DB update failed for variant {label}: {db_err}")
                    return {"label": label, "status": "error", "error": {"type": "db_error", "message": str(db_err)}}

                if wait_time:
                    await asyncio.sleep(wait_time)  # optional pacing between variants

                return {"label": label, "status": "ok", "data": refined_result}

            except asyncio.TimeoutError:
                logger.error(f"Timeout refining variant {label}: exceeded {per_request_timeout}s")
                return {
                    "label": label,
                    "status": "error",
                    "error": {"type": "timeout", "message": f"did not complete within {per_request_timeout}s"},
                }
            except Exception as e:
                logger.error(f"Unhandled error refining variant {label}: {e}")
                return {"label": label, "status": "error", "error": {"type": "unhandled", "message": str(e)}}

    def _normalize_structured_prompt(self, result_data: Dict[str, Any], shot_type: str) -> None:
        # CHANGE: normalize structured_prompt returned from API if it's a JSON string
        sp_field = result_data.get("structured_prompt")
        if isinstance(sp_field, str):
            try:
                result_data["structured_prompt"] = json.loads(sp_field)
            except json.JSONDecodeError:
                logger.warning(f"structured_prompt not valid JSON for {shot_type}; leaving as string")

    async def _execute_generation(
        self,
        *,
        shot_type: str,
        semaphore: asyncio.Semaphore,
        per_request_timeout: int,
        wait_time: int,
        call_coro_fn: Callable[[], Awaitable[Dict[str, Any]]],
        build_saved_data: Callable[[Dict[str, Any]], Dict[str, Any]],
        persist_fn: Callable[[Dict[str, Any]], None],
    ) -> Dict[str, Any]:
        async with semaphore:
            try:
                result_data = await asyncio.wait_for(call_coro_fn(), timeout=per_request_timeout)

                if isinstance(result_data, dict) and "error" in result_data:
                    logger.error(f"Client returned error for {shot_type}: {result_data['error']}")
                    return {"shot_type": shot_type, "status": "error", "error": result_data["error"]}

                self._normalize_structured_prompt(result_data, shot_type)

                try:
                    envelope = build_saved_data(result_data)
                    persist_fn(envelope)
                except Exception as db_err:
                    logger.error(f"DB insert failed for {shot_type}: {db_err}")
                    return {
                        "shot_type": shot_type,
                        "status": "error",
                        "error": {"type": "db_error", "message": str(db_err)},
                    }

                if wait_time:
                    await asyncio.sleep(wait_time)
                return {"shot_type": shot_type, "status": "ok", "data": result_data}

            except asyncio.TimeoutError:
                logger.error(f"Timeout for {shot_type}: exceeded {per_request_timeout}s")
                return {
                    "shot_type": shot_type,
                    "status": "error",
                    "error": {"type": "timeout", "message": f"did not complete within {per_request_timeout}s"},
                }
            except Exception as e:
                logger.error(f"Unhandled error for {shot_type}: {e}")
                return {"shot_type": shot_type, "status": "error", "error": {"type": "unhandled", "message": str(e)}}

    # ========= Generation =========
    async def generate_one(
        self,
        shot_type: str,
        item: Dict[str, Any],
        image_gen_client: ImageGenClient,
        images_collection: GeneratedImagesCollection,
        semaphore: asyncio.Semaphore,
        wait_time: int,
        per_request_timeout: int,
        generation_method: Literal["structured_prompt", "text"],
        db_save_fn: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        # CHANGE: Generate a single shot with explicit generation_method and pluggable persistence.
        Do not raise; return an error dict so the batch continues.
        item is data from the LLM (text) or user input (structured JSON).
        """
        if generation_method == "text":
            text_prompt = item.get("prompt", "")
            reasoning = item.get("reasoning", "")
            if not text_prompt:
                logger.error(f"Skipping shot '{shot_type}': empty prompt")
                return {"shot_type": shot_type, "status": "error", "error": {"type": "input_error", "message": "empty prompt"}}

            logger.info(
                f"Generating image for {shot_type} with prompt (len={len(text_prompt)}): {text_prompt[:200]}"
            )

            return await self._execute_generation(
                shot_type=shot_type,
                semaphore=semaphore,
                per_request_timeout=per_request_timeout,
                wait_time=wait_time,
                call_coro_fn=lambda: image_gen_client.create_image_from_text(
                    text_prompt=text_prompt,
                    model_version="FIBO",
                ),
                build_saved_data=lambda result_data: {
                    "result_data": result_data,
                    "generation_data": {"text_prompt": text_prompt, "reasoning": reasoning},
                    "shot_type": shot_type,
                },
                persist_fn=images_collection.insert_data,
            )

        # structured_prompt branch
        user_structured_prompt = item.get("structured_prompt") or item.get("user_structured_prompt")
        if not user_structured_prompt:
            logger.error(
                f"Skipping shot '{shot_type}': missing structured_prompt for generation_method=structured_prompt"
            )
            return {
                "shot_type": shot_type,
                "status": "error",
                "error": {"type": "input_error", "message": "missing structured_prompt"},
            }

        logger.info(f"Generating image for {shot_type} from structured_prompt")

        return await self._execute_generation(
            shot_type=shot_type,
            semaphore=semaphore,
            per_request_timeout=per_request_timeout,
            wait_time=wait_time,
            call_coro_fn=lambda: image_gen_client.create_image_from_structured_prompt(
                structured_prompt=user_structured_prompt,
                model_version="FIBO",
            ),
            build_saved_data=lambda result_data: {
                "result_data": result_data,
                "generation_data": {"structured_prompt": user_structured_prompt, "source": "user_json_edit"},
                "shot_type": shot_type,
            },
            persist_fn=db_save_fn if db_save_fn else images_collection.insert_data,  # CHANGE: allow per-call persistence
        )

    # ========= Setup / Planning =========
    def setup(self):
        self.image_bytes = get_image_bytes(self.uploaded_image)
        logger.info(f"Loaded image bytes from {self.uploaded_image}")

    def get_prompts(self):
        prompts = translate_vision_to_image_prompt(self.vision, self.image_bytes)
        self.prompts = prompts.response.model_dump()
        if not isinstance(self.prompts, dict) or not self.prompts:
            logger.error("No prompts returned from translation step; skipping generation")
            self.prompts = {}

    def get_variants(self):
        # CHANGE: convert variant strings to dicts with variant_label and description for better semantics
        variants = {
            "lighting": [
                {"variant_label": "softbox_even", "description": "Large softbox, minimal shadows, gentle wrap, even illumination"},
                {"variant_label": "strong_directional", "description": "Strong directional light from behind or side, crisp shadows, dramatic rim highlights"},
                {"variant_label": "backlit_glow", "description": "Light source behind product, glowing edges, caustics/refractions for glass/liquid."},
                {"variant_label": "low_angle_sunset", "description": "Low-angle, warm color temperature, long soft shadows, sunset vibe"},
                {"variant_label": "blue_window", "description": "Blue-toned, shadowless, natural window light, neutral/cool palette"},
            ]
        }
        self.variants = variants

    # ========= Orchestration =========
    async def create_variants(
        self,
        image_gen_client: ImageGenClient,
        images_collection: GeneratedImagesCollection,
        seed: str,
        request_id: str,
        structured_prompt: Dict[str, Any],
        selected_variant_label: str,  # just one for now
        wait_time: int,
        max_concurrency: int = 4,
        per_request_timeout: int = 120,
    ) -> List[Dict[str, Any]]:
        selected_variant_list = self.variants.get(selected_variant_label, [])
        semaphore = asyncio.Semaphore(max_concurrency)
        tasks: List[asyncio.Task] = [
            asyncio.create_task(
                self.refine_one(
                    seed=seed,
                    structured_prompt=structured_prompt,
                    request_id=request_id,
                    variant_item=v,
                    image_gen_client=image_gen_client,
                    images_collection=images_collection,
                    semaphore=semaphore,
                    wait_time=wait_time,
                    per_request_timeout=per_request_timeout,
                )
            )
            for v in selected_variant_list
        ]
        return await asyncio.gather(*tasks)

    async def generate_images(
        self,
        image_gen_client: ImageGenClient,
        images_collection: GeneratedImagesCollection,
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
                    generation_method="text",
                )
            )
            for k, v in self.prompts.items()
        ]

        return await asyncio.gather(*tasks)  # CHANGE: tasks return dicts; no exceptions bubble here

    async def run_json_edit(
        self,
        image_gen_client: ImageGenClient,
        images_collection: GeneratedImagesCollection,
        request_id: str,  # to store
        shot_type: str,
        user_structured_prompt: Dict[str, Any],
        wait_time: int = 0,  # top level functions so add defaults here
        per_request_timeout: int = 120,
    ) -> Dict[str, Any]:
        semaphore = asyncio.Semaphore(1)  # just one bc we are just running once
        prompt_data = {"user_structured_prompt": user_structured_prompt}

        def request_id_wrapper(saved_data: Dict[str, Any]):
            images_collection.update_image_with_edit(request_id=request_id, edited_image_data=saved_data)

        return await self.generate_one(
            shot_type=shot_type,  # pass from frontend in request
            item=prompt_data,
            image_gen_client=image_gen_client,
            images_collection=images_collection,
            semaphore=semaphore,
            wait_time=wait_time,
            per_request_timeout=per_request_timeout,
            generation_method="structured_prompt",
            db_save_fn=request_id_wrapper,
        )

    async def run_variant_gen(
        self,
        image_gen_client: ImageGenClient,
        images_collection: GeneratedImagesCollection,
        seed: str,
        request_id: str,
        structured_prompt: Dict[str, Any],
        selected_variant_label: str,  # just one for now
        wait_time: int,
        max_concurrency: int = 4,
        per_request_timeout: int = 120,
    ) -> List[Dict[str, Any]]:
        self.get_variants()
        return await self.create_variants(
            image_gen_client=image_gen_client,
            images_collection=images_collection,
            seed=seed,
            request_id=request_id,
            structured_prompt=structured_prompt,
            selected_variant_label=selected_variant_label,
            wait_time=wait_time,
            max_concurrency=max_concurrency,
            per_request_timeout=per_request_timeout,
        )

    async def run_initial_gen(
        self,
        image_gen_client: ImageGenClient,
        images_collection: GeneratedImagesCollection,
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


# Example manual usage (kept commented for reference)
# async def main():
#     from app.db.db_connection import DatabaseConnection
#     from app.db.db_collections import GeneratedImagesCollection
#     db = DatabaseConnection.get_instance()
#     db.initialize_mongo_client()
#     images_collection = GeneratedImagesCollection()
#     image_gen_client = get_image_gen_client()
#     image_path = "./input_images/tech_drawing_sample.png"
#     vision = "Oriental maximalism, vibrant, gold accents, intricate patterns"
#     orchestrator = ImageGenOrchestrator(vision, image_path)
#     result = await orchestrator.run_initial_gen(
#         image_gen_client=image_gen_client,
#         images_collection=images_collection,
#     )
#     return result
# if __name__ == "__main__":
#     res = asyncio.run(main())
#     print(res)
#     db.initialize_mongo_client()

#     images_collection= GeneratedImagesCollection()

