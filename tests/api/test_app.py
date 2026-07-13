from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from clinical_inference_workstation.api.app import create_app


def _build_sample_image_bytes() -> bytes:
    image = Image.new("RGB", (96, 96), (220, 220, 220))
    draw = ImageDraw.Draw(image)
    draw.ellipse((18, 18, 78, 78), fill=(232, 88, 88))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_health_endpoint_should_report_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_endpoint_should_return_signals_probability_and_bucket() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/v1/analyze",
        files={"image": ("sample.png", _build_sample_image_bytes(), "image/png")},
    )

    payload = response.json()

    assert response.status_code == 200
    assert payload["decision"]["bucket"] in {"routine_monitor", "review_soon", "urgent_review"}
    assert payload["signals"]["redness_ratio"] > 0.0
    assert 0.0 <= payload["model"]["calibrated_probability"] <= 1.0


def test_analyze_endpoint_should_return_localized_region_for_overlay() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/v1/analyze",
        files={"image": ("sample.png", _build_sample_image_bytes(), "image/png")},
    )

    region = response.json()["region"]

    assert 0 <= region["x0"] < region["x1"] <= 96
    assert 0 <= region["y0"] < region["y1"] <= 96
    assert region["image_width"] == 96
    assert region["image_height"] == 96
