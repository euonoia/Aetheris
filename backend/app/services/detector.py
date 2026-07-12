from ultralytics import YOLO
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")
OUTPUT_DIR = os.path.join(BASE_DIR, "app", "outputs")

model = YOLO(MODEL_PATH)


def detect_image(image_path: str, confidence_threshold: float = 0.25):
    """Run YOLO on `image_path` and return detections filtered by vehicle classes

    Args:
        image_path: local path to the uploaded image
        confidence_threshold: minimum confidence to include a detection

    Returns:
        Tuple of (detections, output_path)

    Notes:
        - Only detections with class_id in VEHICLE_CLASSES are returned.
        - `result.save()` still writes the full annotated image.
    """
    # run inference
    results = model(image_path)
    result = results[0]

    detections = []

    # Allowed COCO class IDs for vehicles
    VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

    # Iterate detections and filter by class and confidence
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        # Skip non-vehicle classes
        if class_id not in VEHICLE_CLASSES:
            continue

        # Skip detections below the confidence threshold
        if confidence < float(confidence_threshold):
            continue

        class_name = VEHICLE_CLASSES[class_id]

        # Convert bounding box tensor to ints: [x1, y1, x2, y2]
        xyxy = box.xyxy[0].tolist()
        bounding_box = [int(x) for x in xyxy]

        detections.append({
            "class_id": class_id,
            "class_name": class_name,
            # Round confidence to 2 decimals as requested
            "confidence": round(confidence, 2),
            "bounding_box": bounding_box,
        })

    # Save annotated image (same behavior as before). Use _detected suffix.
    original_name = os.path.basename(image_path)
    name, ext = os.path.splitext(original_name)
    output_filename = f"{name}_detected{ext}"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    result.save(filename=output_path)

    return detections, output_path