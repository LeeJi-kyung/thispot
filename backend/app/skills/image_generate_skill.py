"""Generate badge images by compositing: AI-generated background + original character.

Three-step approach:
  1. Gemini Vision extracts ONE key non-human visual element from walk photos.
  2. Gemini Flash generates a background-only scene (no character).
  3. Pillow composites the original character (main.png) onto the background.
"""

import io
import json
import os
import re
from pathlib import Path

from PIL import Image

try:
    from google import genai as _genai
    from google.genai import types as _gtypes

    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

_CHAR_REF_PATH = Path(__file__).resolve().parents[3] / "main.png"

# ── Step 1: key element extraction ───────────────────────────────────────────

_KEYWORD_EXTRACT_PROMPT = """\
The user's target color is: {target_color}.

Look at this image and find the single most visually prominent NON-HUMAN element \
that is {target_color} in color or closely related to {target_color}.
Ignore any people. Focus on objects, nature, scenery, architecture, or weather phenomena.

Return ONLY valid JSON, no markdown, no explanation:

{{
  "key_element": "one specific {target_color} object or prop the character could hold or interact with (e.g. 'a red apple', 'a blue umbrella', 'a yellow sunflower bouquet', 'an orange popsicle')",
  "scene_desc": "background scene visible behind the character (e.g. 'a sunny beach with blue ocean waves', 'a snowy park with white trees', 'cherry blossom path in spring')",
  "action": "what the character is doing — keep it simple and physical (e.g. 'holding a blue umbrella', 'eating an orange popsicle', 'sitting under cherry blossoms')",
  "colors": "specific shades of {target_color} present (e.g. 'deep crimson and warm orange')",
  "mood": "the mood or atmosphere (e.g. 'serene', 'dreamy', 'warm and cozy')"
}}
"""

# ── Step 2: image-edit prompt (sent together with main.png) ───────────────────

_EDIT_PROMPT_TMPL = """\
Edit this image of a chibi character.

DO NOT change anything about the character herself — \
her face, eyes, hair, skin, expression, and body proportions must stay identical.

Make only these changes:
1. Change the background to: {scene_desc}
2. Add to her hands or nearby: {key_element} (she is {action})
3. Color palette: {colors}. Mood: {mood}.

Keep the 3D soft clay toy style consistent throughout.\
"""


def _parse_keywords(text: str) -> dict:
    clean = re.sub(r"```(?:json)?\s*|```", "", text).strip()
    return json.loads(clean)


def extract_structured_keywords(photo_paths: list[Path], api_key: str, target_color: str = "") -> list[dict]:
    """Use Gemini Vision to extract the target-color-related element from each walk photo."""
    if not _HAS_GENAI or not photo_paths:
        return []

    client = _genai.Client(api_key=api_key)
    results: list[dict] = []
    prompt = _KEYWORD_EXTRACT_PROMPT.format(target_color=target_color or "dominant")

    for path in photo_paths[:5]:
        try:
            buf = io.BytesIO()
            Image.open(path).convert("RGB").save(buf, format="PNG")
            img_part = _gtypes.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, img_part],
            )
            kw = _parse_keywords(response.text)
            results.append(kw)
            print(f"[badge-gen] key element from {path.name}: {kw}")
        except Exception as e:
            print(f"[badge-gen] extraction failed for {path.name}: {e}")

    return results


def build_badge_prompt(title: str, color: str, rarity: str, keywords: list[dict] | None = None) -> str:
    """Build image-edit prompt to send alongside main.png."""
    if keywords:
        best = max(keywords, key=lambda k: len(k.get("key_element", "")))
        key_element = best.get("key_element") or f"a {color} object"
        scene_desc = best.get("scene_desc") or f"a {color} outdoor environment"
        action = best.get("action") or f"holding a {color} object"
        colors = best.get("colors") or color
        mood = best.get("mood") or "serene"
    else:
        key_element = f"a {color} object"
        scene_desc = f"a {color} outdoor environment"
        action = f"holding a {color} object"
        colors = color
        mood = "serene"

    return _EDIT_PROMPT_TMPL.format(
        key_element=key_element,
        scene_desc=scene_desc,
        action=action,
        colors=colors,
        mood=mood,
    )


def _save_as_9x16(image_bytes: bytes, output_path: Path, target_w: int = 900) -> None:
    """Crop and resize image to 9:16 aspect ratio, then save."""
    img = Image.open(io.BytesIO(image_bytes))
    w, h = img.size
    target_h = int(target_w * 16 / 9)
    target_ratio = 9 / 16

    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    img = img.resize((target_w, target_h), Image.LANCZOS)
    img.save(output_path, format="PNG")


def generate_badge_image(prompt: str, output_path: Path) -> bool:
    """Send main.png + edit prompt to Gemini Flash; it edits the image in-place."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not _HAS_GENAI:
        return False

    if not _CHAR_REF_PATH.exists():
        print(f"[badge-gen] character reference not found at {_CHAR_REF_PATH}")
        return False

    try:
        client = _genai.Client(api_key=api_key)

        char_buf = io.BytesIO()
        Image.open(_CHAR_REF_PATH).convert("RGB").save(char_buf, format="PNG")
        char_part = _gtypes.Part.from_bytes(data=char_buf.getvalue(), mime_type="image/png")

        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[char_part, prompt],
            config=_gtypes.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                _save_as_9x16(part.inline_data.data, output_path)
                print(f"[badge-gen] edited badge saved to {output_path}")
                return True

        print("[badge-gen] Gemini Flash returned no image")
        return False

    except Exception as e:
        print(f"[badge-gen] Flash edit failed: {e}")
        return False
