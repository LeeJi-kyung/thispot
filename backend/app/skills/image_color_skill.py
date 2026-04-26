from __future__ import annotations

from pathlib import Path


class ImageColorSkill:
    def sample_pixels(self, image_path: str | Path, max_size: tuple[int, int] = (220, 220)) -> list[tuple[int, int, int]]:
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        image.thumbnail(max_size)
        return list(image.getdata())

    def dominant_palette(self, image_path: str | Path) -> list[tuple[int, int, int]]:
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        image.thumbnail((220, 220))
        palette_image = image.quantize(colors=6, method=Image.Quantize.MEDIANCUT)
        palette = palette_image.getpalette() or []
        colors = palette_image.getcolors(maxcolors=220 * 220) or []
        colors.sort(reverse=True)

        result: list[tuple[int, int, int]] = []
        for _, index in colors:
            offset = index * 3
            rgb = tuple(palette[offset: offset + 3])
            if len(rgb) == 3:
                result.append((int(rgb[0]), int(rgb[1]), int(rgb[2])))
        return result or [(59, 130, 246)]
