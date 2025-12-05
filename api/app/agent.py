from app.utils.utils_lib import format_prompt
from app.utils.image_utils import create_image_input
from google.genai import types
from app.services.genai_client import google_client
from app.utils.response_handlers import handle_llm_response, ResponseSuccess
from pydantic import BaseModel, Field
from typing import List, Type, TypeVar
from app.utils.decorators import retry_on_failure

# ========= Schema Models =========
class PromptItem(BaseModel):
    prompt: str
    reasoning: str

class ImagePrompts(BaseModel):
    hero: PromptItem
    detail: PromptItem
    environment: PromptItem
    flatlay: PromptItem

class VariantItem(BaseModel):
    variant_label: str = Field(..., description="Snake_case label for the variant option")
    description: str = Field(..., description="Concise professional description (8–18 words)")

class ImageVariants(BaseModel):
    lighting: List[VariantItem] = Field(..., description="Lighting setups tuned for material and reflectivity")
    camera: List[VariantItem] = Field(..., description="Camera viewpoints and angles")
    composition: List[VariantItem] = Field(..., description="Framing and placement patterns")
    surface: List[VariantItem] = Field(..., description="Product support surfaces and environments")
    color_grade: List[VariantItem] = Field(..., description="Color grading options")
    background: List[VariantItem] = Field(..., description="Backdrop styling")
    mood: List[VariantItem] = Field(..., description="Atmospheric tone presets")

class VariantGroups(BaseModel):
    groups: ImageVariants = Field(..., description="Top-level schema grouping all variant categories")


T = TypeVar("T", bound=BaseModel)

def _call_gemini_with_image(
    *,
    image_bytes: bytes,
    user_prompt: str,
    system_prompt_path: str,
    response_schema: Type[T],
) -> ResponseSuccess:
    system_instruction = format_prompt(system_prompt_path)
    image_input = create_image_input(image_bytes)
    user_input = types.Part.from_text(text=user_prompt)
    
    generation_config = types.GenerateContentConfig(
        response_schema=response_schema,
        response_mime_type="application/json",
        system_instruction=system_instruction,
    )
    
    contents = types.Content(role="user", parts=[image_input, user_input])
    response = google_client.models.generate_content(
        model="gemini-2.5-pro",
        contents=contents,
        config=generation_config,
    )
    
    handle_llm_response(response, response_attr="parsed")
    return ResponseSuccess(response=response.parsed)


@retry_on_failure()
def translate_vision_to_image_prompt(vision: str, image_bytes: bytes) -> ResponseSuccess:
    """
    # CHANGE: Generate 4-shot plan (hero/detail/environment/flatlay) from vision + image.
    """
    user_prompt = f"""
Based on the following theme/vision statement generate a set of detailed image prompts suitable for an AI image generation model. 
Each prompt should include specific details about the subject, style, colors, and composition to create a vivid and engaging image.
The required styles that the images should follow are:
1. Hero Image: A striking and dynamic image that captures the essence of the vision. 
2. Detail Image: A close-up image focusing on details.
3. Environment Image: An image that places the subject within a relevant and immersive environment.
4. Flatlay Image: A top-down view showcasing the subject in a styled arrangement.
VISION: {vision}
You also have access to the reference image, which you must use to inform the style and composition of the generated prompts.
"""
    return _call_gemini_with_image(
        image_bytes=image_bytes,
        user_prompt=user_prompt,
        system_prompt_path="./app/prompts/translate_to_image_prompt_v2.txt",
        response_schema=ImagePrompts,
    )

@retry_on_failure()
def plan_variants(image_bytes: bytes, shot_type: str) -> ResponseSuccess:
    """
    # CHANGE: Generate dynamic variant schema (lighting/camera/composition/etc.) for given shot_type.
    """
    user_prompt = f"""
Context:
- The shot_type is: "{shot_type}"
- Use what you see in the image: subject material (glass/metal/fabric/leather), reflectivity/translucency, current lighting quality and direction, camera viewpoint (pitch/yaw/height), background style (solid/gradient/props), and overall mood.

Requirements:
- Return ONLY valid JSON.
- Produce 5 variants per group, tailored to the image and shot_type.
- variant_label: snake_case, 1–3 words, concise (e.g., "softbox_even", "low_hero").
- description: 8–18 words, professional, actionable, no marketing fluff.
- Keep options distinct and production-safe (avoid extreme effects or busy props).
- Hero shots: prioritize three_quarter, low_hero, clean lighting.
- Detail shots: prefer macro_detail, tight_crop, controlled highlights.
- Flatlay: keep pitch top-down; avoid extreme yaw; favor center_clean.
- Environment: background can include subtle props or gradients; keep subject dominant.
"""
    return _call_gemini_with_image(
        image_bytes=image_bytes,
        user_prompt=user_prompt,
        system_prompt_path="./app/prompts/plan_variants.txt",
        response_schema=VariantGroups,
    )

# if __name__=="__main__":
#     from app.utils.image_utils import get_image_bytes
#     image_path="./input_images/tech_drawing_sample.png"
#     vision="Minimal luxury"
#     image_bytes= get_image_bytes(image_path)
#     response= translate_vision_to_image_prompt(vision, image_bytes)
#     print(response.model_dump())