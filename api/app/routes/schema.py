from fastapi import APIRouter
from app.config.variant_registry import get_variants

router = APIRouter(prefix="/schema")


@router.get("/variants")
async def list_variants():
	"""Return the supported variant schema (single source of truth)."""
	return get_variants()

