from PIL import Image, ImageDraw

from clinical_inference_workstation.ml.features import extract_visual_signals, locate_signal_region


def test_should_locate_red_region_bounding_box() -> None:
    image = Image.new("RGB", (96, 96), (210, 210, 210))
    draw = ImageDraw.Draw(image)
    draw.ellipse((30, 10, 80, 60), fill=(235, 70, 70))

    region = locate_signal_region(image)

    assert abs(region.x0 - 30) <= 4
    assert abs(region.y0 - 10) <= 4
    assert abs(region.x1 - 80) <= 4
    assert abs(region.y1 - 60) <= 4
    assert region.coverage > 0.1


def test_should_fall_back_to_central_region_when_no_red_signal_present() -> None:
    image = Image.new("RGB", (96, 96), (210, 210, 210))

    region = locate_signal_region(image)

    assert 0 <= region.x0 < region.x1 <= 96
    assert 0 <= region.y0 < region.y1 <= 96
    assert region.coverage == 0.0


def test_should_report_high_redness_when_central_region_is_red() -> None:
    image = Image.new("RGB", (96, 96), (210, 210, 210))
    draw = ImageDraw.Draw(image)
    draw.ellipse((18, 18, 78, 78), fill=(235, 70, 70))

    signals = extract_visual_signals(image)

    assert signals.redness_ratio > 0.3


def test_should_report_higher_texture_when_image_contains_dense_speckles() -> None:
    image = Image.new("RGB", (96, 96), (205, 205, 205))
    draw = ImageDraw.Draw(image)
    for x in range(14, 82, 8):
        for y in range(14, 82, 8):
            draw.rectangle((x, y, x + 2, y + 2), fill=(35, 35, 35))

    signals = extract_visual_signals(image)

    assert signals.texture_score > 0.03

