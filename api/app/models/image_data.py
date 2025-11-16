from pydantic import BaseModel, ConfigDict
from typing import Dict
from datetime import datetime
from pydantic import Field
class ResultData(BaseModel):
    image_url:str
    seed: int
    structured_prompt: Dict[str, any]
    saved_path: str
    request_id: str
    model_config = ConfigDict(extra="allow")

class GenerationData(BaseModel):
    text_prompt: str
    reasoning: str
    model_config = ConfigDict(extra="allow")

class ImageData(BaseModel):
    result_data: ResultData
    generation_data: GenerationData
    shot_type: str
    timestamp: datetime = Field(default_factory=datetime.now)

