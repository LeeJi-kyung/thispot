from __future__ import annotations

import io
import json
import os
import re
from pathlib import Path

from PIL import Image


try:
    from google import genai
    from google.genai import types

    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


APP_DIR = Path(__file__).resolve().parents[1]
CHARACTER_DIR = APP_DIR / "assets" / "character"
CHARACTER_IMAGE_CANDIDATES = [
    CHARACTER_DIR / "main.png",
    CHARACTER_DIR / "base.png",
]


KEYWORD_EXTRACT_PROMPT = """\
The user's target color is: {target_color}.

Look at this image and find the single most visually prominent NON-HUMAN element
that is {target_color} in color or closely related to {target_color}.
Ignore any people. Focus on objects, nature, scenery, architecture, or weather phenomena.

Return ONLY valid JSON, no markdown, no explanation:

{{
  "key_element": "one specific {target_color} object or prop the character could hold or interact with",
  "scene_desc": "background scene visible behind the character",
  "action": "what the character is doing; keep it simple and physical",
  "colors": "specific shades of {target_color} present",
  "mood": "the mood or atmosphere"
}}
"""


EDIT_PROMPT_TEMPLATE = """\
Edit this image of a chibi character.

Do not change the character's face, eyes, hair, expression, body proportions,
or core identity.

Make only these changes:
1. Change the background to: {scene_desc}
2. Add to the character's hands or nearby: {key_element}; the character is {action}
3. Color palette: {colors}. Mood: {mood}.

Keep the soft 3D clay toy style consistent. Return a polished vertical reward image.
"""


def extract_structured_keywords(
    photo_paths: list[Path],
    *,
    api_key: str,
    target_color: str,
) -> list[dict]:
    if not HAS_GENAI or not api_key:
        return []

    client = genai.Client(api_key=api_key)
    prompt = KEYWORD_EXTRACT_PROMPT.format(target_color=target_color)
    results: list[dict] = []

    for path in photo_paths[:5]:
        try:
            buffer = io.BytesIO()
            Image.open(path).convert("RGB").save(buffer, format="PNG")
            image_part = types.Part.from_bytes(data=buffer.getvalue(), mime_type="image/png")
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=[prompt, image_part],
            )
            results.append(_parse_json(getattr(response, "text", "") or ""))
        except Exception as error:
            print(f"[image-generate] keyword extraction failed for {path.name}: {error}")

    return results


def build_badge_prompt(
    *,
    color: str,
    keywords: list[dict] | None = None,
) -> str:
    if keywords:
        selected = max(keywords, key=lambda item: len(str(item.get("key_element", ""))))
        key_element = selected.get("key_element") or f"a {color} object"
        scene_desc = selected.get("scene_desc") or f"a {color} outdoor environment"
        action = selected.get("action") or f"holding a {color} object"
        colors = selected.get("colors") or color
        mood = selected.get("mood") or "bright and playful"
    else:
        key_element = f"a {color} mission object"
        scene_desc = f"a playful {color} outdoor color-hunt scene"
        action = f"holding a {color} object"
        colors = color
        mood = "bright and playful"

    return EDIT_PROMPT_TEMPLATE.format(
        key_element=key_element,
        scene_desc=scene_desc,
        action=action,
        colors=colors,
        mood=mood,
    )


def generate_badge_image(prompt: str, output_path: Path) -> bool:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not HAS_GENAI:
        return False

    character_path = _character_reference_path()
    if character_path is None:
        print("[image-generate] character reference image not found")
        return False

    try:
        client = genai.Client(api_key=api_key)
        character_buffer = io.BytesIO()
        Image.open(character_path).convert("RGB").save(character_buffer, format="PNG")
        character_part = types.Part.from_bytes(
            data=character_buffer.getvalue(),
            mime_type="image/png",
        )

        response = client.models.generate_content(
            model=os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview"),
            contents=[character_part, prompt],
            config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
        )

        for candidate in response.candidates or []:
            for part in candidate.content.parts or []:
                if part.inline_data is None:
                    continue
                output_path.parent.mkdir(parents=True, exist_ok=True)
                _save_vertical_png(part.inline_data.data, output_path)
                return output_path.exists()
    except Exception as error:
        print(f"[image-generate] image generation failed: {error}")

    return False


def _parse_json(text: str) -> dict:
    clean = re.sub(r"```(?:json)?\s*|```", "", text).strip()
    return json.loads(clean)


def _character_reference_path() -> Path | None:
    for path in CHARACTER_IMAGE_CANDIDATES:
        if path.exists():
            return path
    return None


def _save_vertical_png(image_bytes: bytes, output_path: Path, target_width: int = 900) -> None:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size
    target_ratio = 9 / 16
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    elif current_ratio < target_ratio:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))

    target_height = int(target_width * 16 / 9)
    image = image.resize((target_width, target_height), Image.LANCZOS)
    image.save(output_path, format="PNG")
