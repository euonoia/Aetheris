import os
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from main import OUTPUT_DIR, UPLOAD_DIR, app


client = TestClient(app)


def test_detect_image_upload_saves_file():
    image = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    response = client.post(
        "/detect-image",
        files={"file": ("test.png", image_bytes, "image/png")},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["detections"], list)
    assert "image_url" in data
    assert "total_vehicle_detections" in data
    assert "vehicle_statistics" in data

    saved_path = os.path.join(UPLOAD_DIR, data["filename"])
    assert os.path.exists(saved_path)

    output_filename = os.path.basename(data["image_url"])
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    assert os.path.exists(output_path)

    os.remove(saved_path)
    os.remove(output_path)
