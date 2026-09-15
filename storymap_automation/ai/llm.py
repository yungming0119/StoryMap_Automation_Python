import base64
import io

import requests

from storymap_automation.config import LM_MODEL, LM_STUDIO_URL

SYSTEM_PROMPT = (
    "You write short, factual transportation summaries. You MUST format numbers with "
    "commas, and you MUST use the Oxford comma in lists. You MUST NOT use markdown formatting."
)

def call_gemma(prompt, image_path=None, image_obj=None):
    content = [
        {"type": "text", "text": prompt}
    ]

    # If user passed a PIL image object
    if image_obj is not None:
        buf = io.BytesIO()
        image_obj.save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{b64}"
            }
        })

    # If user passed a file path
    elif image_path is not None:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{b64}"
            }
        })

    payload = {
        "model": LM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": content},
        ],
        "ReasoningEffort": "none",
    }

    try:
        response = requests.post(
            LM_STUDIO_URL,
            json=payload,
        )
        response.raise_for_status()
        response_data = response.json()
    except (requests.RequestException, ValueError) as exc:
        return f"[LLM Error] {exc}"

    choices = response_data.get("choices")
    if not choices or not isinstance(choices[0], dict):
        return f"[LLM Error] {response_data}"

    message = choices[0].get("message", {})
    result = message.get("content")
    if result is None:
        return f"[LLM Error] {response_data}"

    return result
