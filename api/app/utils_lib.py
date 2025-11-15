def format_prompt(template_path: str, **kwargs) -> str:
    """Replace {{variable}} placeholders in template with kwargs"""
    with open(template_path, "r") as f:
        template = f.read()

    # Replace all {{key}} with values from kwargs
    for key, value in kwargs.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))

    return template