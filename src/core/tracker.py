"""Simple inference timing tracker with detection history."""
from collections import deque
from typing import Dict, Any, List
import statistics


class InferenceTracker:
    """Track inference times and detection counts over time."""

    def __init__(self, max_history: int = 500) -> None:
        self.max_history = max_history
        self._times: deque = deque(maxlen=max_history)
        self._models: deque = deque(maxlen=max_history)
        self._detect_counts: deque = deque(maxlen=max_history)

    def record(self, inference_ms: float, model: str = "", detection_count: int = 0) -> None:
        """Record a single inference run."""
        self._times.append(inference_ms)
        self._models.append(model)
        self._detect_counts.append(detection_count)

    def summary(self) -> Dict[str, Any]:
        """Return aggregated statistics."""
        if not self._times:
            return {"count": 0, "avg_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0, "fps": 0.0}
        avg_ms = statistics.mean(self._times)
        return {
            "count": len(self._times),
            "avg_ms": round(avg_ms, 2),
            "min_ms": round(min(self._times), 2),
            "max_ms": round(max(self._times), 2),
            "fps": round(1000.0 / avg_ms, 2) if avg_ms > 0 else 0.0,
        }

    def recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Return the last N records as a list of dicts."""
        records = list(zip(self._times, self._models, self._detect_counts))
        return [
            {"inference_ms": t, "model": m, "detections": d}
            for t, m, d in records[-n:]
        ]

    def to_dataframe(self) -> "pandas.DataFrame":
        """Return the full history as a pandas DataFrame."""
        import pandas as pd
        records = list(zip(self._times, self._models, self._detect_counts))
        return pd.DataFrame(records, columns=["inference_ms", "model", "detections"])