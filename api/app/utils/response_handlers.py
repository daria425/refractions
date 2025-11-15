from typing import Any, Optional, Literal
from pydantic import BaseModel
from app.utils.logger import logger


class ResponseSuccess(BaseModel):
    success: bool = True
    response: Any


class ResponseFailure(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None


def handle_llm_response(
    response,
    response_attr: Literal["parsed", "text", "output_parsed"],
):
    value = getattr(response, response_attr, None)
    if value is None:
        logger.warning("Response parsing failed.")
        raise ValueError("Failed to parse response")