from fastapi import Body, APIRouter, Depends, HTTPException
from app.utils.logger import logger
from app.image_orchestrator import ImageGenOrchestrator
from app.image_gen_client import get_image_gen_client
from app.db.db_collections import GeneratedImagesCollection
from app.models.image_data import VariantGenRequestBody
from app.utils.image_utils import get_image_bytes
from app.agent import improve_image

router=APIRouter(prefix="/shots")
@router.post("/{request_id}/variants/{selected_variant_label}")
async def run_variant_generation(
    request_id: str,
    selected_variant_label: str,
    body: VariantGenRequestBody = Body(...),
    images_collection: GeneratedImagesCollection = Depends(GeneratedImagesCollection),
):
    try:
        orchestrator = ImageGenOrchestrator()
        image_gen_client = get_image_gen_client()

        results = await orchestrator.run_variant_gen(
            image_gen_client=image_gen_client,
            images_collection=images_collection,
            seed=body.seed,
            request_id=request_id,
            structured_prompt=body.structured_prompt,
            selected_variant_label=selected_variant_label,
            wait_time=0,
            max_concurrency=4,
            per_request_timeout=120,
        )

        successes = [r for r in results if r.get("status") == "ok"]
        failures = [r for r in results if r.get("status") == "error"]
        return {
            "status": "completed",
            "total": len(results),
            "successful": len(successes),
            "failed": len(failures),
            "results": results,
            "message": f"Variants {selected_variant_label}: {len(successes)}/{len(results)} ok",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Variant gen failed: {e}")
        raise HTTPException(status_code=500, detail=f"Variant generation failed: {str(e)}")
    
@router.get("/{request_id}/critique")
async def improve_img_from_critique(request_id:str, images_collection:GeneratedImagesCollection=Depends(GeneratedImagesCollection)):
        orchestrator = ImageGenOrchestrator()
        image_gen_client = get_image_gen_client()
        requested_image=images_collection.get_image_by_request_id(request_id=request_id)
        logger.info(f"Fetching image with {requested_image["result_data"]["saved_path"]} URL")
        image_bytes=get_image_bytes(requested_image["result_data"]["saved_path"])
        shot_type=requested_image["shot_type"]
        seed=requested_image["result_data"]["seed"]
        prev_structured_prompt=requested_image["result_data"]["structured_prompt"]
        generation_details=requested_image["generation_data"]
        refinement_run_data=improve_image(shot_type=shot_type, image_bytes=image_bytes, generation_details=generation_details)
        refined_prompt=refinement_run_data["refinement"]
        critique=refinement_run_data["critique"]
        refinement_data={
             "description": refined_prompt,
             "variant_label": "ai_refinement"
        }
        metadata={
             "critique": critique
        }
        result=await orchestrator.refine_image_variant(seed=seed, structured_prompt=prev_structured_prompt, request_id=request_id, variant_item=refinement_data, image_gen_client=image_gen_client, images_collection=images_collection, metadata=metadata)
        return result



