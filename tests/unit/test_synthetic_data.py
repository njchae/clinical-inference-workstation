import math

from PIL import ImageStat

from clinical_inference_workstation.ml.synthetic_data import generate_synthetic_case


def test_should_generate_deterministic_case_metadata_for_a_fixed_seed() -> None:
    case = generate_synthetic_case(seed=7, image_size=96)

    assert case.case_id == "case-0007"
    assert case.image.size == (96, 96)
    assert isinstance(case.has_concerning_pattern, bool)
    assert 0.0 <= case.redness_level <= 1.0


def test_should_expose_lesion_bbox_within_image_bounds() -> None:
    case = generate_synthetic_case(seed=7, image_size=96)

    x0, y0, x1, y1 = case.lesion_bbox

    assert 0 <= x0 < x1 <= 96
    assert 0 <= y0 < y1 <= 96
    assert (x1 - x0) * (y1 - y0) >= 96 * 96 * 0.05


def test_should_render_textured_lesion_interior_even_without_speckles() -> None:
    config = {
        "redness_min": 0.6,
        "redness_max": 0.6,
        "texture_min": 0.0,
        "texture_max": 0.0,
        "extent_min": 0.4,
        "extent_max": 0.4,
    }

    case = generate_synthetic_case(seed=3, image_size=96, generation_config=config)

    x0, y0, x1, y1 = case.lesion_bbox
    inset_x = (x1 - x0) // 4
    inset_y = (y1 - y0) // 4
    interior = case.image.crop((x0 + inset_x, y0 + inset_y, x1 - inset_x, y1 - inset_y))
    red_stddev = ImageStat.Stat(interior).stddev[0]
    assert red_stddev > 4.0


def test_should_draw_irregular_lesion_boundary_rather_than_a_perfect_circle() -> None:
    case = generate_synthetic_case(seed=11, image_size=96)

    image = case.image.convert("RGB")
    center = 48
    radii: list[int] = []
    for step in range(36):
        angle = step * (2 * math.pi / 36)
        boundary = 0
        for distance in range(1, 48):
            x = int(center + distance * math.cos(angle))
            y = int(center + distance * math.sin(angle))
            if 0 <= x < 96 and 0 <= y < 96:
                red, green, blue = image.getpixel((x, y))
                if red > green + 20 and red > blue + 20:
                    boundary = distance
        radii.append(boundary)

    mean_radius = sum(radii) / len(radii)
    radius_stddev = (sum((radius - mean_radius) ** 2 for radius in radii) / len(radii)) ** 0.5
    assert radius_stddev > 1.2

