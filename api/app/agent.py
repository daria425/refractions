from app.utils.utils_lib import format_prompt
from app.utils.image_utils import create_image_input
from google.genai import types
from app.genai_client import google_client
from app.utils.response_handlers import handle_llm_response, ResponseSuccess
from pydantic import BaseModel
from app.utils.decorators import retry_on_failure

class ImagePrompts(BaseModel):
    hero:str
    detail:str
    environment:str
    flatlay:str

@retry_on_failure()
def translate_vision_to_image_prompt(vision:str, image_bytes: bytes) -> ResponseSuccess:
    prompt_path="./app/prompts/translate_to_image_prompt_v2.txt"
    system_instruction = format_prompt(prompt_path)
    image_input = create_image_input(image_bytes)
    user_input = types.Part.from_text(
        text=f"""
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
    )
    generation_config = types.GenerateContentConfig(
        response_schema=ImagePrompts, response_mime_type="application/json", system_instruction=system_instruction
    )
    contents = types.Content(role="user", parts=[image_input, user_input])
    response = google_client.models.generate_content(
        model="gemini-2.5-pro",
        contents=contents,
        config=generation_config,
    )
    handle_llm_response(response, response_attr="parsed")
    return ResponseSuccess(response=response.parsed)

if __name__=="__main__":
    from app.utils.image_utils import get_image_bytes
    image_path="./input_images/tech_drawing_sample.png"
    vision="Minimal luxury"
    image_bytes= get_image_bytes(image_path)
    response= translate_vision_to_image_prompt(vision, image_bytes)
    print(response.model_dump())