from __future__ import annotations

from dataclasses import dataclass
from random import Random

import numpy as np
from PIL import Image

from clinical_inference_workstation.config import load_synthetic_data_config


@dataclass(frozen=True)
class SyntheticCase:
    case_id: str
    image: Image.Image
    redness_level: float
    texture_level: float
    lesion_extent: float
    has_concerning_pattern: bool
    lesion_bbox: tuple[int, int, int, int]


def _smooth_noise_field(noise_rng: np.random.Generator, size: int, cell: int = 8) -> np.ndarray:
    coarse_side = max(size // cell, 2)
    coarse = noise_rng.normal(0.0, 1.0, size=(coarse_side, coarse_side))
    field = np.kron(coarse, np.ones((cell, cell)))[:size, :size]
    kernel = np.ones(5) / 5.0
    field = np.apply_along_axis(lambda row: np.convolve(row, kernel, mode="same"), 1, field)
    field = np.apply_along_axis(lambda col: np.convolve(col, kernel, mode="same"), 0, field)
    return field


def generate_synthetic_case(
    seed: int,
    image_size: int = 96,
    generation_config: dict | None = None,
) -> SyntheticCase:
    rng = Random(seed)
    config = generation_config or load_synthetic_data_config()["generation"]
    redness_level = round(rng.uniform(config["redness_min"], config["redness_max"]), 4)
    texture_level = round(rng.uniform(config["texture_min"], config["texture_max"]), 4)
    lesion_extent = round(rng.uniform(config["extent_min"], config["extent_max"]), 4)
    has_concerning_pattern = rng.random() >= 0.5

    noise_rng = np.random.default_rng(seed)

    center_x = image_size / 2.0 + rng.uniform(-3.0, 3.0)
    center_y = image_size / 2.0 + rng.uniform(-3.0, 3.0)
    base_radius = image_size * (0.28 + lesion_extent * 0.10)

    boundary_waves = [
        (2, rng.uniform(0.05, 0.09), rng.uniform(0.0, 6.28)),
        (3, rng.uniform(0.03, 0.06), rng.uniform(0.0, 6.28)),
        (5, rng.uniform(0.02, 0.05), rng.uniform(0.0, 6.28)),
    ]

    yy, xx = np.mgrid[0:image_size, 0:image_size].astype(float)
    dx = xx - center_x
    dy = yy - center_y
    distance = np.hypot(dx, dy)
    theta = np.arctan2(dy, dx)

    radius_at_theta = np.full_like(theta, base_radius)
    for frequency, amplitude, phase in boundary_waves:
        radius_at_theta = radius_at_theta + base_radius * amplitude * np.sin(frequency * theta + phase)

    lesion_alpha = np.clip((radius_at_theta - distance) / 1.5, 0.0, 1.0)
    lesion_mask = lesion_alpha > 0.5

    background_gradient = (yy / image_size - 0.5) * 6.0
    background_noise = _smooth_noise_field(noise_rng, image_size, cell=12) * 2.0
    background = np.stack(
        [
            226.0 + background_noise + background_gradient,
            223.0 + background_noise + background_gradient,
            218.0 + background_noise + background_gradient,
        ],
        axis=-1,
    )

    base_red = 170.0 + redness_level * 70.0
    base_green = 130.0 - redness_level * 60.0
    base_blue = 130.0 - redness_level * 55.0

    mottle = _smooth_noise_field(noise_rng, image_size, cell=6)
    mottle_amplitude = 0.05 + 0.12 * texture_level
    shading = 1.0 + mottle * mottle_amplitude

    edge_falloff = np.clip((radius_at_theta - distance) / (0.45 * base_radius), 0.0, 1.0)
    depth = 0.74 + 0.26 * edge_falloff

    lesion = np.stack(
        [
            base_red * shading * depth,
            base_green * shading * depth,
            base_blue * shading * depth,
        ],
        axis=-1,
    )

    speckle_count = int(texture_level * 140)
    speckle_field = np.ones((image_size, image_size))
    for _ in range(speckle_count):
        sx = rng.uniform(center_x - base_radius * 0.8, center_x + base_radius * 0.8)
        sy = rng.uniform(center_y - base_radius * 0.8, center_y + base_radius * 0.8)
        spot_radius = rng.uniform(1.0, 2.4)
        spot = np.exp(-(((xx - sx) ** 2 + (yy - sy) ** 2) / (2.0 * spot_radius**2)))
        speckle_field = speckle_field * (1.0 - 0.45 * spot)
    lesion = lesion * speckle_field[..., None]

    if has_concerning_pattern:
        ring_radius = radius_at_theta * 0.55
        ring_band = np.abs(distance - ring_radius) < max(2.2, image_size / 36.0)
        ring_gaps = np.sin(theta * 7.0 + rng.uniform(0.0, 6.28)) > -0.8
        ring_mask = ring_band & ring_gaps
        lesion = np.where(ring_mask[..., None], lesion * 0.35, lesion)

        slash = np.abs((dy * 0.8 + dx * 0.6)) < max(1.8, image_size / 44.0)
        slash_extent = distance < base_radius * 0.42
        slash_mask = slash & slash_extent
        lesion = np.where(slash_mask[..., None], lesion * 0.4, lesion)

    composed = background * (1.0 - lesion_alpha[..., None]) + lesion * lesion_alpha[..., None]
    pixels = np.clip(composed, 0.0, 255.0).astype(np.uint8)
    image = Image.fromarray(pixels, mode="RGB")

    mask_rows = np.any(lesion_mask, axis=1)
    mask_cols = np.any(lesion_mask, axis=0)
    row_indices = np.where(mask_rows)[0]
    col_indices = np.where(mask_cols)[0]
    lesion_bbox = (
        int(col_indices.min()),
        int(row_indices.min()),
        int(col_indices.max()) + 1,
        int(row_indices.max()) + 1,
    )

    return SyntheticCase(
        case_id=f"case-{seed:04d}",
        image=image,
        redness_level=redness_level,
        texture_level=texture_level,
        lesion_extent=lesion_extent,
        has_concerning_pattern=has_concerning_pattern,
        lesion_bbox=lesion_bbox,
    )


def export_sample_cases(samples_dir, manifest_path) -> list[dict[str, str]]:
    synthetic_config = load_synthetic_data_config()
    image_size = synthetic_config["dataset"]["image_size"]
    generation_config = synthetic_config["generation"]
    samples_dir.mkdir(parents=True, exist_ok=True)

    examples: list[dict[str, str]] = []
    for case_config in synthetic_config["sample_cases"]:
        case = generate_synthetic_case(
            seed=case_config["seed"],
            image_size=image_size,
            generation_config=generation_config,
        )
        image_name = f"{case.case_id}.png"
        case.image.save(samples_dir / image_name, format="PNG")
        examples.append(
            {
                "case_id": case.case_id,
                "label": case_config["label"],
                "description": case_config["description"],
                "image_url": f"/workstation/samples/{image_name}",
            }
        )

    manifest_path.write_text(__import__("json").dumps(examples, indent=2), encoding="utf-8")
    return examples
