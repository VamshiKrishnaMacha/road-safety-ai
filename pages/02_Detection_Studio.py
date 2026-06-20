"""02_Detection_Studio.py — Flagship interactive detection page."""
import os
import sys
import io
import json
import hashlib
from datetime import datetime
from typing import Optional

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.components.layout import inject_custom_css, page_header
from src.core.engine import YOLOEngine, DetectionResult
from src.utils.exporters import export_detections_json, export_detections_csv, export_image_bytes

# ---------------------------------------------------------------------------
# CSS & Header
# ---------------------------------------------------------------------------
inject_custom_css()
page_header("Detection Studio", "Interactive AI-powered road marking detection")

# ---------------------------------------------------------------------------
# Project root helper
# ---------------------------------------------------------------------------
def get_project_root() -> str:
    """Return absolute path to project root (parent of pages/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scan_models() -> list[str]:
    """Return all .pt model files in the project root."""
    root = get_project_root()
    return sorted([f for f in os.listdir(root) if f.endswith(".pt")])


# ---------------------------------------------------------------------------
# Engine loading (with session caching)
# ---------------------------------------------------------------------------
def load_engine(model_path: str, conf: float, iou: float) -> YOLOEngine:
    """Load or retrieve cached YOLOEngine from session state."""
    cache_key = f"engine_{model_path}"
    if cache_key not in st.session_state:
        engine = YOLOEngine(model_path=model_path, conf=conf, iou=iou)
        engine.load()
        st.session_state[cache_key] = engine
    engine = st.session_state[cache_key]
    engine.conf = conf
    engine.iou = iou
    return engine


# ---------------------------------------------------------------------------
# Failed case saving
# ---------------------------------------------------------------------------
def save_feedback(
    image: np.ndarray,
    detections: list,
    model: str,
    correct: bool,
) -> None:
    """Save image and detections to failed_cases/ for later review."""
    failed_dir = os.path.join(get_project_root(), "failed_cases")
    os.makedirs(failed_dir, exist_ok=True)

    prefix = "correct" if correct else "incorrect"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    hash_name = hashlib.md5(image.tobytes()[:1000]).hexdigest()[:8]
    base = f"{prefix}_{ts}_{hash_name}"

    # Save image
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    pil_img.save(os.path.join(failed_dir, f"{base}.jpg"), quality=85)

    # Save detections as JSON
    with open(os.path.join(failed_dir, f"{base}.json"), "w") as f:
        json.dump({"model": model, "detections": detections}, f, indent=2)


# ---------------------------------------------------------------------------
# Scan available models
# ---------------------------------------------------------------------------
available_models = scan_models()
if not available_models:
    st.warning("No .pt model files found in the project root. Add a model to proceed.")
    st.stop()

# Ensure active_model is initialised
if "active_model" not in st.session_state or st.session_state.active_model not in available_models:
    st.session_state.active_model = available_models[0]


# ---------------------------------------------------------------------------
# Top Controls Row — Model settings left, file uploader right
# ---------------------------------------------------------------------------
left_col, right_col = st.columns([0.3, 0.7])

with left_col:
    # Model selector
    selected_model = st.selectbox(
        "Model",
        available_models,
        index=available_models.index(st.session_state.active_model),
        help="Select a YOLO model for inference",
    )
    st.session_state.active_model = selected_model

    model_path = os.path.join(get_project_root(), selected_model)
    try:
        model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
        st.caption(f"Model: {model_size_mb:.1f} MB")
    except OSError:
        st.caption("Model file not found locally.")

    # Confidence slider
    conf = st.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        value=st.session_state.settings.get("conf", 0.25),
        help="Minimum confidence score for a detection to be retained",
    )
    st.session_state.settings["conf"] = conf

    # IoU slider
    iou = st.slider(
        "IoU Threshold",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        value=st.session_state.settings.get("iou", 0.45),
        help="Intersection over Union threshold for Non-Maximum Suppression",
    )
    st.session_state.settings["iou"] = iou

with right_col:
    uploaded_file = st.file_uploader(
        "Upload an image to begin detection",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG, PNG",
    )
    if uploaded_file is None:
        st.info("Upload an image using the uploader above, then detection will run automatically.")


# ---------------------------------------------------------------------------
# State placeholders
# ---------------------------------------------------------------------------
original_image: Optional[np.ndarray] = None
annotated_image: Optional[np.ndarray] = None
result: Optional[DetectionResult] = None

# ---------------------------------------------------------------------------
# Inference (when file is present)
# ---------------------------------------------------------------------------
if uploaded_file is not None:
    # Load image
    bytes_data = uploaded_file.getvalue()
    pil_img = Image.open(io.BytesIO(bytes_data)).convert("RGB")
    original_image = np.array(pil_img)

    # Inference caching key
    run_key = f"inf_{uploaded_file.name}_{selected_model}_{conf:.2f}_{iou:.2f}"

    if run_key not in st.session_state:
        try:
            engine = load_engine(selected_model, conf, iou)
            result = engine.predict_image(original_image)
            st.session_state[run_key] = result
            st.session_state.tracker.record(result.inference_ms, selected_model, len(result.boxes))
            st.session_state.class_names = engine.get_class_names()
        except Exception as e:
            st.error(f"Inference failed: {e}")
            result = None
    else:
        result = st.session_state[run_key]

    # Annotated image
    if result is not None and result.annotated_image is not None:
        annotated_image = result.annotated_image

    # -------------------------------------------------------------------------
    # Before / After Tabs
    # -------------------------------------------------------------------------
    tab_original, tab_detection = st.tabs(["Original", "Detection"])

    with tab_original:
        st.image(original_image, channels="RGB", use_container_width=True)

    with tab_detection:
        if annotated_image is not None:
            st.image(annotated_image, channels="BGR", use_container_width=True)
        elif result is not None and result.boxes:
            st.info("No annotated image available, but detections were found.")
        else:
            st.info("Run inference to see detection results.")

    # -------------------------------------------------------------------------
    # Detection Statistics
    # -------------------------------------------------------------------------
    st.markdown("### Detection Statistics")

    if result is not None:
        col_stats1, col_stats2 = st.columns(2)
        with col_stats1:
            st.metric("Total Objects", len(result.boxes))
        with col_stats2:
            st.metric("Inference Time", f"{result.inference_ms:.1f} ms")

        if result.class_counts:
            st.markdown("**Class Breakdown**")
            breakdown_data = {
                "Class": list(result.class_counts.keys()),
                "Count": list(result.class_counts.values()),
            }
            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
    else:
        st.info("No detection results available.")

    # -------------------------------------------------------------------------
    # Per-Detection Details Table
    # -------------------------------------------------------------------------
    if result is not None and result.boxes:
        st.markdown("### Per-Detection Details")

        # Class filter
        all_classes = st.session_state.get("class_names", [])
        selected_classes = st.multiselect(
            "Filter by Class",
            options=all_classes,
            default=[],
            help="Show only these classes (leave empty for all)",
        )

        display_boxes = result.boxes
        if selected_classes:
            display_boxes = [b for b in display_boxes if b["cls"] in selected_classes]

        det_rows = []
        for b in display_boxes:
            det_rows.append({
                "Class": b["cls"],
                "Confidence": f"{b['conf']:.3f}",
                "X1": b["x1"],
                "Y1": b["y1"],
                "X2": b["x2"],
                "Y2": b["y2"],
            })

        det_df = pd.DataFrame(det_rows)
        st.dataframe(det_df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # Export Row
    # -------------------------------------------------------------------------
    st.markdown("### Export Results")

    dl_col1, dl_col2, dl_col3 = st.columns(3)

    with dl_col1:
        if annotated_image is not None:
            img_bytes = export_image_bytes(annotated_image, fmt="PNG")
            st.download_button(
                "Download Image (PNG)",
                data=img_bytes,
                file_name="detection_output.png",
                mime="image/png",
                use_container_width=True,
            )

    with dl_col2:
        if result is not None and result.boxes:
            json_str = export_detections_json(result.boxes)
            st.download_button(
                "Download JSON",
                data=json_str,
                file_name="detections.json",
                mime="application/json",
                use_container_width=True,
            )

    with dl_col3:
        if result is not None and result.boxes:
            csv_str = export_detections_csv(result.boxes)
            st.download_button(
                "Download CSV",
                data=csv_str,
                file_name="detections.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # -------------------------------------------------------------------------
    # Feedback Buttons
    # -------------------------------------------------------------------------
    st.markdown("### Feedback")

    fb_col1, fb_col2 = st.columns(2)

    with fb_col1:
        if st.button("Prediction Correct", use_container_width=True):
            if annotated_image is not None and result is not None:
                save_feedback(annotated_image, result.boxes, selected_model, correct=True)
                st.success("Saved to failed_cases/ as a correct prediction.")
            else:
                st.warning("No detection result available to save.")

    with fb_col2:
        if st.button("Prediction Incorrect", use_container_width=True):
            if annotated_image is not None and result is not None:
                save_feedback(annotated_image, result.boxes, selected_model, correct=False)
                st.success("Saved to failed_cases/ for review.")
            else:
                st.warning("No detection result available to save.")