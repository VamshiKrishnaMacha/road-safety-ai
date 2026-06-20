"""Export utilities for detections."""
import json
import csv
import io
import base64
from typing import List, Dict, Any
import numpy as np


def export_detections_json(detections: List[Dict[str, Any]]) -> str:
    """Export detections as a structured JSON string."""
    records = []
    for det in detections:
        records.append({
            "class": det.get("cls", ""),
            "confidence": det.get("conf", 0.0),
            "bbox": {
                "x1": det.get("x1", 0),
                "y1": det.get("y1", 0),
                "x2": det.get("x2", 0),
                "y2": det.get("y2", 0),
            },
        })
    payload = {
        "total_detections": len(records),
        "detections": records,
    }
    return json.dumps(payload, indent=2)


def export_detections_csv(detections: List[Dict[str, Any]]) -> str:
    """Export detections as a CSV string with structured columns."""
    if not detections:
        return "class,confidence,x1,y1,x2,y2\n"
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["class", "confidence", "x1", "y1", "x2", "y2"],
    )
    writer.writeheader()
    for det in detections:
        writer.writerow({
            "class": det.get("cls", ""),
            "confidence": det.get("conf", 0.0),
            "x1": det.get("x1", 0),
            "y1": det.get("y1", 0),
            "x2": det.get("x2", 0),
            "y2": det.get("y2", 0),
        })
    return output.getvalue()


def export_image_bytes(image: np.ndarray, fmt: str = "PNG") -> bytes:
    """Convert a numpy image array to PNG bytes.

    Accepts either RGB or BGR numpy arrays and converts appropriately.
    """
    from PIL import Image
    # If image has 3 channels, assume BGR from ultralytics and convert to RGB
    if len(image.shape) == 3 and image.shape[2] == 3:
        import cv2
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_image)
    else:
        pil_img = Image.fromarray(image)
    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    return buf.getvalue()