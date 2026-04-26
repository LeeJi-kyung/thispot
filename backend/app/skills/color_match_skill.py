from __future__ import annotations

import colorsys
import math


COLOR_RGB = {
    "red": (239, 68, 68),
    "orange": (249, 115, 22),
    "yellow": (234, 179, 8),
    "green": (34, 197, 94),
    "blue": (59, 130, 246),
    "violet": (139, 92, 246),
    "white": (241, 245, 249),
    "black": (15, 23, 42),
}


class ColorMatchSkill:
    MAX_RGB_DISTANCE = math.sqrt(3 * (255 ** 2))
    HUE_RANGES = {
        "red": [(345, 360), (0, 15)],
        "orange": [(16, 40)],
        "yellow": [(41, 65)],
        "green": [(66, 165)],
        "blue": [(190, 250)],
        "violet": [(276, 320)],
    }

    def score(self, detected_color: str, target_color: str) -> float:
        return 0.87 if detected_color.lower() == target_color.lower() else 0.42

    def detected_color(self, palette: list[tuple[int, int, int]]) -> str:
        if not palette:
            return "blue"
        return self._nearest_color(palette[0])

    def detected_color_from_pixels(
        self,
        pixels: list[tuple[int, int, int]],
        palette: list[tuple[int, int, int]] | None = None,
    ) -> str:
        if not pixels:
            return self.detected_color(palette or [])

        scores = {
            color: self._target_ratio(pixels, color)
            for color in COLOR_RGB
        }
        if scores["black"] >= 0.60:
            return "black"
        if scores["white"] >= 0.60:
            return "white"
        color, ratio = max(scores.items(), key=lambda item: item[1])
        if ratio >= 0.08:
            return color
        return self.detected_color(palette or [])

    def score_palette(self, palette: list[tuple[int, int, int]], target_color: str) -> float:
        target = COLOR_RGB.get(target_color.lower(), COLOR_RGB["blue"])
        best_distance = min((self._distance(rgb, target) for rgb in palette), default=self.MAX_RGB_DISTANCE)
        score = max(0.0, 1.0 - (best_distance / self.MAX_RGB_DISTANCE))
        return round(score, 2)

    def score_pixels(self, pixels: list[tuple[int, int, int]], target_color: str) -> float:
        target = target_color.lower()
        if target not in COLOR_RGB or not pixels:
            return 0.0

        ratio = self._target_ratio(pixels, target)
        distance_score = self._nearest_distance_score(pixels, target)
        score = max(ratio, (ratio * 0.80) + (distance_score * 0.20))
        return round(min(1.0, score), 2)

    def _target_ratio(self, pixels: list[tuple[int, int, int]], target_color: str) -> float:
        valid_count = 0
        match_count = 0
        for pixel in pixels:
            hue, saturation, value = self._hsv(pixel)
            if not self._is_valid_pixel(target_color, saturation, value):
                continue
            valid_count += 1
            if self._matches_target(target_color, hue, saturation, value):
                match_count += 1
        if valid_count == 0:
            return 0.0
        return match_count / valid_count

    def _nearest_distance_score(self, pixels: list[tuple[int, int, int]], target_color: str) -> float:
        if target_color in {"white", "black"}:
            target_rgb = COLOR_RGB[target_color]
            best_distance = min((self._distance(pixel, target_rgb) for pixel in pixels), default=self.MAX_RGB_DISTANCE)
            return max(0.0, 1.0 - (best_distance / self.MAX_RGB_DISTANCE))

        distances: list[float] = []
        for pixel in pixels:
            hue, saturation, value = self._hsv(pixel)
            if saturation < 0.18 or value < 0.15:
                continue
            distances.append(self._hue_distance_to_range(hue, self.HUE_RANGES[target_color]))
        if not distances:
            return 0.0
        return max(0.0, 1.0 - (min(distances) / 180))

    def _is_valid_pixel(self, target_color: str, saturation: float, value: float) -> bool:
        if target_color == "white":
            return value >= 0.55
        if target_color == "black":
            return value <= 0.45
        return saturation >= 0.18 and value >= 0.15

    def _matches_target(self, target_color: str, hue: float, saturation: float, value: float) -> bool:
        if target_color == "white":
            return saturation <= 0.22 and value >= 0.78
        if target_color == "black":
            return value <= 0.24
        return any(start <= hue <= end for start, end in self.HUE_RANGES[target_color])

    @staticmethod
    def _hsv(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
        red, green, blue = (channel / 255 for channel in rgb)
        hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
        return hue * 360, saturation, value

    @staticmethod
    def _hue_distance_to_range(hue: float, ranges: list[tuple[int, int]]) -> float:
        if any(start <= hue <= end for start, end in ranges):
            return 0.0
        distances = []
        for start, end in ranges:
            distances.extend([
                abs(hue - start),
                abs(hue - end),
                360 - abs(hue - start),
                360 - abs(hue - end),
            ])
        return min(distances)

    def _nearest_color(self, rgb: tuple[int, int, int]) -> str:
        return min(COLOR_RGB, key=lambda color: self._distance(rgb, COLOR_RGB[color]))

    @staticmethod
    def _distance(left: tuple[int, int, int], right: tuple[int, int, int]) -> float:
        return math.sqrt(sum((left[index] - right[index]) ** 2 for index in range(3)))
