from fastapi import APIRouter, Depends
from app.config.variant_registry import get_variants
from app.db.db_collections import GeneratedImagesCollection
from app.utils.image_utils import get_image_bytes
from app.utils.logger import logger
from app.agent import plan_variants
router = APIRouter(prefix="/schema")



@router.get("/variants")
async def list_variants():
	"""Return the supported variant schema (single source of truth)."""
	return get_variants()


@router.get("/variants/{request_id}")
async def get_variants_for_image(request_id:str, generated_images_collection:GeneratedImagesCollection=Depends(GeneratedImagesCollection)):
	requested_image=generated_images_collection.get_image_by_request_id(request_id=request_id)
	logger.info(f"Fetching image with {requested_image["result_data"]["saved_path"]} URL")
	image_bytes=get_image_bytes(requested_image["result_data"]["saved_path"])
	shot_type=requested_image["shot_type"]
	variants_resp=plan_variants(image_bytes=image_bytes, shot_type=shot_type)
	variants=variants_resp.response.model_dump()
	logger.info(f"Recieved variants {variants}")
	formatted_variants={
		"version": "v1", 
		"groups":variants["groups"]
	}
	return formatted_variants
