
from typing import Dict, Any

_VARIANTS: Dict[str, Any] = {
    "version": "v1",
    "groups": {
        "lighting": [
            {"variant_label": "softbox_even", "description": "Large softbox, minimal shadows, gentle wrap, even illumination"},
            {"variant_label": "strong_directional", "description": "Strong directional light from behind or side, crisp shadows, dramatic rim highlights"},
            {"variant_label": "backlit_glow", "description": "Light source behind product, glowing edges, caustics/refractions for glass/liquid."},
            {"variant_label": "low_angle_sunset", "description": "Low-angle, warm color temperature, long soft shadows, sunset vibe"},
            {"variant_label": "blue_window", "description": "Blue-toned, shadowless, natural window light, neutral/cool palette"},
        ],
    },
}

def get_variants() -> Dict[str, Any]:
    return _VARIANTS