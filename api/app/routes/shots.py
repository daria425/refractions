# CHANGE: add route to trigger variant generation
from fastapi import Body, APIRouter, Depends, HTTPException
from app.utils.logger import logger
from app.image_orchestrator import ImageGenOrchestrator
from app.image_gen_client import get_image_gen_client
from app.db.db_collections import GeneratedImagesCollection
from app.models.image_data import VariantGenRequestBody

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
        image_gen_client = get_image_gen_client()  # CHANGE: instantiate client

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