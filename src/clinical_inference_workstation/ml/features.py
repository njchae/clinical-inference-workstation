from __future__ import annotations

from dataclasses import asdict, dataclass

from PIL import Image, ImageStat


@dataclass(frozen=True)
class VisualSignals:
    redness_ratio: float
    texture_score: float
    lesion_extent: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class SignalRegion:
    x0: int
    y0: int
    x1: int
    y1: int
    coverage: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def locate_signal_region(image: Image.Image) -> SignalRegion:
    rgb_image = image.convert("RGB")
    width, height = rgb_image.size

    working = rgb_image.copy()
    working.thumbnail((256, 256))
    working_width, working_height = working.size
    scale_x = width / working_width
    scale_y = height / working_height

    min_x, min_y = working_width, working_height
    max_x = max_y = -1
    signal_pixels = 0
    for index, (red, green, blue) in enumerate(working.getdata()):
        if red > green + 20 and red > blue + 20:
            signal_pixels += 1
            x = index % working_width
            y = index // working_width
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    if signal_pixels == 0:
        return SignalRegion(
            x0=width // 6,
            y0=height // 6,
            x1=width - width // 6,
            y1=height - height // 6,
            coverage=0.0,
        )

    coverage = signal_pixels / (working_width * working_height)
    return SignalRegion(
        x0=int(min_x * scale_x),
        y0=int(min_y * scale_y),
        x1=min(int((max_x + 1) * scale_x), width),
        y1=min(int((max_y + 1) * scale_y), height),
        coverage=round(coverage, 4),
    )


def extract_visual_signals(image: Image.Image) -> VisualSignals:
    rgb_image = image.convert("RGB")
    width, height = rgb_image.size
    center_box = (
        width // 6,
        height // 6,
        width - width // 6,
        height - height // 6,
    )
    focus_region = rgb_image.crop(center_box)
    stat = ImageStat.Stat(focus_region)
    r_mean, g_mean, b_mean = stat.mean
    gray_stddev = ImageStat.Stat(focus_region.convert("L")).stddev[0]

    total = max(r_mean + g_mean + b_mean, 1.0)
    redness_ratio = max((r_mean - ((g_mean + b_mean) / 2.0)) / total * 3.0, 0.0)
    texture_score = gray_stddev / 255.0

    lesion_pixels = 0
    total_pixels = focus_region.size[0] * focus_region.size[1]
    for red, green, blue in focus_region.getdata():
        if red > green + 20 and red > blue + 20:
            lesion_pixels += 1

    lesion_extent = lesion_pixels / max(total_pixels, 1)
    return VisualSignals(
        redness_ratio=round(redness_ratio, 4),
        texture_score=round(texture_score, 4),
        lesion_extent=round(lesion_extent, 4),
    )

