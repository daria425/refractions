# CHANGE: Lightweight async test to verify structured_prompt round-trip equality
import os
import json
import pytest

from app.image_gen_client import get_image_gen_client


@pytest.mark.asyncio
async def test_structured_prompt_roundtrip_equal():
    """Ensure the structured_prompt sent matches the one returned in the result.
    Skips when BRIA_API_TOKEN is not configured.
    """
    api_token = os.getenv("BRIA_API_TOKEN")
    if not api_token:
        pytest.skip("BRIA_API_TOKEN not set; skipping integration test")

    client = get_image_gen_client()

    structured_prompt = {
        "aesthetics": {
            "aesthetic_score": "very high",
            "color_scheme": "Monochromatic and analogous, dominated by soft neutrals (dusty taupe, light stone, off-white) with subtle accents of black and white from the dress pattern and muted pastels from the background blossoms. The overall palette is serene and sophisticated.",
            "composition": "Full-length portrait composition, with the model centered and filling the frame vertically, adhering to a 4:5 aspect ratio. The lines of the dress and the model's posture create leading lines that draw the eye upwards.",
            "mood_atmosphere": "Elegant, serene, sophisticated, and subtly artistic with a touch of ethereal beauty.",
            "preference_score": "very high",
        },
        "artistic_style": "realistic",
        "background_setting": "A minimalist studio environment with a simple, textured wall behind the model. The wall is a neutral, light gray or off-white, providing a clean backdrop that allows the dress and model to stand out. Large, soft-focus spring blossoms are subtly integrated into the background, appearing as ethereal blurs of pastel color, suggesting depth and a touch of organic beauty without distracting from the main subject.",
        "context": "This is a concept for a high-fashion editorial photograph, potentially for a luxury fashion magazine or a designer's lookbook, emphasizing the garment's unique design and artistic elements.",
        "lighting": {
            "conditions": "Soft, diffused morning light",
            "direction": "Front-lit, with a gentle glow from the upper-left, mimicking natural window light.",
            "shadows": "Very soft, subtle shadows, particularly around the model's form and the drapes of the dress, adding dimension without harshness. The background blossoms cast almost imperceptible, extremely soft shadows.",
        },
        "objects": [
            {
                "action": "Standing poised, subtly modeling the dress.",
                "appearance_details": "Long, flowing dark brown hair styled naturally, framing her face. Minimal, natural-looking makeup highlighting her features.",
                "clothing": "An asymmetrical, full-length dress in dusty taupe and light stone. It features a single-shoulder drape on her left side, strategic waist cut-outs, and panels embellished with an intricate black and white surreal floral line-art pattern. The fabric appears to have a soft, flowing quality.",
                "description": "A tall, slender female model, embodying elegance and poise, showcasing the intricate details of the dress. Her posture is graceful yet commanding, drawing the viewer's eye to the garment.",
                "expression": "Serene and confident, with a subtle, knowing gaze directed slightly off-camera.",
                "gender": "female",
                "location": "center",
                "orientation": "Facing slightly to her right, body turned three-quarters towards the viewer.",
                "pose": "Standing gracefully, with her left arm slightly bent at the elbow and her hand gently resting on her left hip, and her right arm extended downwards, subtly showcasing the dress's drape. Her weight is shifted slightly to her right leg.",
                "relationship": "The primary subject, interacting directly with the dress and contrasting subtly with the soft background.",
                "relative_size": "large within frame",
                "shape_and_color": "Slender human form, warm skin tones.",
                "skin_tone_and_texture": "Medium-toned, smooth skin with a healthy glow.",
                "texture": "Smooth, radiant skin.",
            },
            {
                "appearance_details": "The line-art pattern features abstract, intertwined floral motifs that appear hand-drawn, creating a dynamic contrast with the solid color blocks. The waist cut-outs are clean and architectural.",
                "description": "The asymmetrical dress is the focal point of the fashion shoot, designed with a sophisticated blend of dusty taupe and light stone colors. Its unique structure includes a single-shoulder drape that cascades elegantly over her left shoulder, precise waist cut-outs that add a modern edge, and distinct panels. These panels are adorned with an intricate, surreal floral line-art pattern in stark black and white, adding a captivating artistic element to the garment.",
                "location": "center",
                "orientation": "Draped and flowing according to the model's pose.",
                "relationship": "Worn by the model, it is the primary subject of the photograph.",
                "relative_size": "large within frame",
                "shape_and_color": "Flowing, asymmetrical silhouette in dusty taupe, light stone, and black and white.",
                "texture": "Smooth, possibly silk or a similar fine fabric, with a soft sheen.",
            },
        ],
        "photographic_characteristics": {
            "camera_angle": "Eye-level, providing a direct and engaging view of the model.",
            "depth_of_field": "Shallow, with the model and dress in sharp focus and the background blossoms rendered in a soft, dreamy bokeh.",
            "focus": "Sharp focus on the model and the intricate details of the dress.",
            "lens_focal_length": "Portrait lens (e.g., 85mm-100mm) to achieve a flattering perspective and good subject isolation.",
        },
        "short_description": "A full-length fashion photograph captures a female model in an asymmetrical dress featuring dusty taupe and light stone colors, a single-shoulder drape, waist cut-outs, and panels adorned with intricate black and white surreal floral line-art. She stands elegantly in a minimalist studio, bathed in soft, diffused morning light, against a textured wall with large, soft-focus spring blossoms, creating a serene and sophisticated visual.",
        "style_medium": "photograph",
    }

    result = await client.create_image_from_structured_prompt(
        structured_prompt=structured_prompt,
        model_version="FIBO",
    )

    if isinstance(result, dict) and "error" in result:
        pytest.fail(f"API error: {result['error']}")

    returned_sp = result.get("structured_prompt")
    if isinstance(returned_sp, str):
        returned_sp = json.loads(returned_sp)

    assert returned_sp == structured_prompt, "Structured prompt mismatch between request and response"
