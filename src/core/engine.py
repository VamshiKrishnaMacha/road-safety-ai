"""YOLO inference engine wrapper with ultralytics."""
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None  # type: ignore


@dataclass
class DetectionResult:
    """Result of a YOLO inference call."""
    boxes: List[Dict[str, Any]]
    class_counts: Dict[str, int]
    annotated_image: Optional[np.ndarray]
    inference_ms: float


class YOLOEngine:
    """Wrapper around ultralytics YOLO model for inference."""

    def __init__(self, model_path: str, conf: float = 0.25, iou: float = 0.45) -> None:
        self.model_path = model_path
        self.conf = conf
        self.iou = iou
        self._model: Optional[Any] = None

    def load(self) -> None:
        """Load the YOLO model from disk."""
        if YOLO is None:
            raise RuntimeError("ultralytics package not installed")
        self._model = YOLO(self.model_path)

    def predict_image(self, image: np.ndarray) -> DetectionResult:
        """Run inference on a single image (HWC RGB format)."""
        return self._run_inference(image)

    def predict_frame(self, frame: np.ndarray) -> DetectionResult:
        """Run inference on a video frame (HWC BGR format)."""
        return self._run_inference(frame)

    def get_class_names(self) -> List[str]:
        """Return the list of class names from the model."""
        if self._model is None:
            self.load()
        return self._model.names if self._model else []

    def _run_inference(self, image: np.ndarray) -> DetectionResult:
        """Internal inference runner. Measures time and extracts results."""
        if self._model is None:
            self.load()

        start = time.perf_counter()
        results = self._model.predict(
            image,
            conf=self.conf,
            iou=self.iou,
            verbose=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        # Extract boxes
        boxes: List[Dict[str, Any]] = []
        if results and len(results) > 0:
            r = results[0]
            if r.boxes is not None:
                for box in r.boxes:
                    xyxy = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    cls_name = self._model.names[cls_id] if self._model else str(cls_id)
                    boxes.append({
                        "x1": int(xyxy[0]),
                        "y1": int(xyxy[1]),
                        "x2": int(xyxy[2]),
                        "y2": int(xyxy[3]),
                        "cls": cls_name,
                        "conf": round(conf, 4),
                    })

        # Count per class
        class_counts: Dict[str, int] = {}
        for b in boxes:
            class_counts[b["cls"]] = class_counts.get(b["cls"], 0) + 1

        # Annotated image — ultralytics returns BGR, keep as-is for cv2 display
        annotated_image: Optional[np.ndarray] = None
        if results and len(results) > 0 and results[0].plot is not None:
            annotated_image = results[0].plot()

        return DetectionResult(
            boxes=boxes,
            class_counts=class_counts,
            annotated_image=annotated_image,
            inference_ms=round(elapsed_ms, 2),
        )