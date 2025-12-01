from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional, Any, Union
from datetime import datetime
from pydantic import Field
class ResultData(BaseModel):
    image_url:str
    seed: int
    structured_prompt: Dict[str, Any]
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

class ImageEditRequestBody(BaseModel):
    image_url:Optional[str]=None
    # below 2 are so that it can be reused
    user_structured_prompt: Optional[Union[Dict[str, Any], str]]=None
    user_text_prompt: Optional[str]=None
    shot_type:str

class VariantGenRequestBody(BaseModel):
    seed:int
    shot_type: str
    structured_prompt: Dict[str, Any]