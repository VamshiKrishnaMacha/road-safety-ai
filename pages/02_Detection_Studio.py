"""02_Detection_Studio.py — Flagship interactive detection page."""
import os
import sys
import io
import json
import hashlib
import base64
from datetime import datetime
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components
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
# Session state helpers
# ---------------------------------------------------------------------------
def _ensure_session_defaults() -> None:
    """Ensure all required session state keys exist."""
    if "settings" not in st.session_state:
        st.session_state.settings = {"conf": 0.25, "iou": 0.45}
    if "tracker" not in st.session_state:
        from src.core.tracker import InferenceTracker
        st.session_state.tracker = InferenceTracker()
    if "zoom_level" not in st.session_state:
        st.session_state.zoom_level = 1.0
    if "dialog_target" not in st.session_state:
        st.session_state.dialog_target = None
    if "class_names" not in st.session_state:
        st.session_state.class_names = []


_ensure_session_defaults()


# ---------------------------------------------------------------------------
# Project root & utilities
# ---------------------------------------------------------------------------
def get_project_root() -> str:
    """Return absolute path to project root (parent of pages/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scan_models() -> list[str]:
    """Return all .pt model files in the project root."""
    root = get_project_root()
    return sorted([f for f in os.listdir(root) if f.endswith(".pt")])


def image_to_base64(img: np.ndarray, is_bgr: bool = False) -> str:
    """Convert numpy array to base64 PNG string."""
    if is_bgr and len(img.shape) == 3 and img.shape[2] == 3:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        rgb = img
    pil = Image.fromarray(rgb)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def format_file_size(size_bytes: int) -> str:
    """Return human-readable file size."""
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


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

    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    pil_img.save(os.path.join(failed_dir, f"{base}.jpg"), quality=85)

    with open(os.path.join(failed_dir, f"{base}.json"), "w") as f:
        json.dump({"model": model, "detections": detections}, f, indent=2)


# ---------------------------------------------------------------------------
# Before/After Slider HTML Builder
# ---------------------------------------------------------------------------
COMPARISON_HTML_TEMPLATE = """
<style>
.comparison-wrapper {{
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 12px;
  cursor: ew-resize;
}}
.comparison-wrapper img {{
  display: block;
  width: 100%;
  height: auto;
  user-select: none;
  -webkit-user-drag: none;
}}
.comparison-overlay {{
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  overflow: hidden;
  border-right: 3px solid #00d4aa;
  z-index: 2;
}}
.comparison-overlay img {{
  max-width: none;
  width: auto;
  height: 100%;
}}
.comparison-handle {{
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  margin-left: -20px;
  margin-top: -20px;
  background: #00d4aa;
  border-radius: 50%;
  z-index: 3;
  cursor: ew-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 15px rgba(0,212,170,0.4);
}}
.comparison-handle::after {{
  content: "\u25C0 \u25B6";
  color: #0a0e17;
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 1px;
}}
</style>
<div id="compare" class="comparison-wrapper">
  <img id="after-img" src="data:image/png;base64,{after_b64}" alt="Detection">
  <div id="overlay" class="comparison-overlay">
    <img id="before-img" src="data:image/png;base64,{before_b64}" alt="Original" style="width:{{container_width}}px;">
  </div>
  <div id="handle" class="comparison-handle"></div>
</div>
<script>
(function() {{
  const wrapper = document.getElementById('compare');
  const overlay = document.getElementById('overlay');
  const handle = document.getElementById('handle');
  const beforeImg = document.getElementById('before-img');

  function updateBeforeWidth() {{
    beforeImg.style.width = wrapper.offsetWidth + 'px';
  }}
  updateBeforeWidth();
  window.addEventListener('resize', updateBeforeWidth);

  let isDragging = false;
  function updateSlider(x) {{
    const rect = wrapper.getBoundingClientRect();
    let pct = ((x - rect.left) / rect.width) * 100;
    pct = Math.min(Math.max(pct, 0), 100);
    overlay.style.width = pct + '%';
    handle.style.left = pct + '%';
  }}
  handle.addEventListener('mousedown', () => isDragging = true);
  window.addEventListener('mouseup', () => isDragging = false);
  window.addEventListener('mousemove', (e) => {{ if (isDragging) updateSlider(e.clientX); }});
  handle.addEventListener('touchstart', (e) => {{ isDragging = true; e.preventDefault(); }});
  window.addEventListener('touchend', () => isDragging = false);
  window.addEventListener('touchmove', (e) => {{
    if (isDragging && e.touches.length > 0) {{ e.preventDefault(); updateSlider(e.touches[0].clientX); }}
  }});
  wrapper.addEventListener('click', (e) => updateSlider(e.clientX));
}})();
</script>
"""


def build_comparison_component(
    before_b64: str,
    after_b64: str,
    container_height: int,
) -> None:
    """Render the interactive before/after slider via streamlit components."""
    html = COMPARISON_HTML_TEMPLATE.format(
        after_b64=after_b64,
        before_b64=before_b64,
    )
    components.html(html, height=container_height)


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
# Scan available models
# ---------------------------------------------------------------------------
available_models = scan_models()
if not available_models:
    st.warning("No .pt model files found in the project root. Add a model to proceed.")
    st.stop()

if "active_model" not in st.session_state or st.session_state.active_model not in available_models:
    st.session_state.active_model = available_models[0]


# ---------------------------------------------------------------------------
# Controls Row (4 columns)
# ---------------------------------------------------------------------------
ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([0.25, 0.25, 0.25, 0.25])

with ctrl1:
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

with ctrl2:
    conf = st.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        value=st.session_state.settings.get("conf", 0.25),
        help="Minimum confidence score for a detection to be retained",
    )
    st.session_state.settings["conf"] = conf

with ctrl3:
    iou = st.slider(
        "IoU Threshold",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        value=st.session_state.settings.get("iou", 0.45),
        help="Intersection-over-Union threshold for Non-Maximum Suppression",
    )
    st.session_state.settings["iou"] = iou

with ctrl4:
    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["jpg", "jpeg", "png"],
        help="Supported: JPG, JPEG, PNG",
    )
    if uploaded_file is None:
        st.info("Upload an image to begin detection.")


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
    bytes_data = uploaded_file.getvalue()
    pil_img = Image.open(io.BytesIO(bytes_data)).convert("RGB")
    original_image = np.array(pil_img)

    run_key = f"inf_{uploaded_file.name}_{selected_model}_{conf:.2f}_{iou:.2f}"

    if run_key not in st.session_state:
        try:
            engine = load_engine(selected_model, conf, iou)
            result = engine.predict_image(original_image)
            st.session_state[run_key] = result
            st.session_state.tracker.record(
                result.inference_ms, selected_model, len(result.boxes)
            )
            st.session_state.class_names = engine.get_class_names()
        except Exception as e:
            st.error(f"Inference failed: {e}")
            result = None
    else:
        result = st.session_state[run_key]

    if result is not None and result.annotated_image is not None:
        annotated_image = result.annotated_image

    # Ensure annotated image matches original dimensions for slider
    if original_image is not None and annotated_image is not None:
        if original_image.shape[:2] != annotated_image.shape[:2]:
            annotated_image = cv2.resize(
                annotated_image,
                (original_image.shape[1], original_image.shape[0]),
            )

    # -------------------------------------------------------------------------
    # Image Comparison Row (side-by-side)
    # -------------------------------------------------------------------------
    left_col, right_col = st.columns([0.5, 0.5])

    with left_col:
        st.markdown("<p style='font-weight:600; margin-bottom:4px;'>Original</p>", unsafe_allow_html=True)
        if original_image is not None:
            st.image(original_image, channels="RGB", use_container_width=True)
            if st.button("Expand Original", use_container_width=True, key="btn_expand_original"):
                st.session_state.dialog_target = "original"
                st.rerun()

    with right_col:
        st.markdown("<p style='font-weight:600; margin-bottom:4px;'>Detection</p>", unsafe_allow_html=True)
        if annotated_image is not None:
            st.image(annotated_image, channels="BGR", use_container_width=True)
            if st.button("Expand Detection", use_container_width=True, key="btn_expand_detection"):
                st.session_state.dialog_target = "detection"
                st.rerun()
        elif result is not None and result.boxes:
            st.info("No annotated image available, but detections were found.")
        else:
            st.info("Run inference to see detection results.")

    # -------------------------------------------------------------------------
    # Fullscreen Modals
    # -------------------------------------------------------------------------
    if st.session_state.dialog_target == "original" and original_image is not None:
        @st.dialog("Original Image")
        def show_original_dialog():
            st.image(original_image, use_container_width=True, caption="Original Image")
            if st.button("Close", key="close_original"):
                st.session_state.dialog_target = None
                st.rerun()
        show_original_dialog()

    if st.session_state.dialog_target == "detection" and original_image is not None:
        @st.dialog("Detection Result")
        def show_detection_dialog():
            display_img = annotated_image if annotated_image is not None else original_image
            channels = "BGR" if annotated_image is not None else "RGB"
            st.image(display_img, use_container_width=True, caption="Detection Result", channels=channels)
            if st.button("Close", key="close_detection"):
                st.session_state.dialog_target = None
                st.rerun()
        show_detection_dialog()

    # -------------------------------------------------------------------------
    # Interactive Before/After Comparison Slider
    # -------------------------------------------------------------------------
    if original_image is not None and annotated_image is not None:
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("<p style='font-weight:600; margin-bottom:4px;'>Interactive Comparison</p>", unsafe_allow_html=True)

        before_b64 = image_to_base64(original_image, is_bgr=False)
        after_b64 = image_to_base64(annotated_image, is_bgr=True)

        nominal_container_width = 700  # approximate full-width Streamlit container
        slider_height = int(
            nominal_container_width
            * original_image.shape[0]
            / original_image.shape[1]
            * st.session_state.zoom_level
        )
        slider_height = max(slider_height, 200)

        build_comparison_component(before_b64, after_b64, slider_height)

    # -------------------------------------------------------------------------
    # Image Zoom Controls Row
    # -------------------------------------------------------------------------
    if original_image is not None and annotated_image is not None:
        st.markdown("<p style='font-weight:600; margin-bottom:4px;'>Zoom Controls</p>", unsafe_allow_html=True)
        z1, z2, z3, z4 = st.columns(4)
        with z1:
            if st.button("Zoom In", use_container_width=True, key="zoom_in"):
                st.session_state.zoom_level = min(st.session_state.zoom_level * 1.25, 5.0)
                st.rerun()
        with z2:
            if st.button("Zoom Out", use_container_width=True, key="zoom_out"):
                st.session_state.zoom_level = max(st.session_state.zoom_level / 1.25, 0.25)
                st.rerun()
        with z3:
            if st.button("Fit Width", use_container_width=True, key="zoom_fit"):
                st.session_state.zoom_level = 1.0
                st.rerun()
        with z4:
            if st.button("Reset View", use_container_width=True, key="zoom_reset"):
                st.session_state.zoom_level = 1.0
                st.rerun()

    # -------------------------------------------------------------------------
    # Image Metadata Bar
    # -------------------------------------------------------------------------
    if original_image is not None:
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("<p style='font-weight:600; margin-bottom:4px;'>Image Metadata</p>", unsafe_allow_html=True)
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric(
                label="Resolution",
                value=f"{original_image.shape[1]} x {original_image.shape[0]}",
            )
        with m2:
            st.metric(
                label="File Size",
                value=format_file_size(uploaded_file.size) if uploaded_file else "—",
            )
        with m3:
            det_count = len(result.boxes) if result is not None else 0
            st.metric(label="Detections", value=det_count)
        with m4:
            inf_ms = f"{result.inference_ms:.1f}" if result is not None else "—"
            st.metric(label="Inference Time", value=f"{inf_ms} ms")
        with m5:
            st.metric(label="Active Model", value=selected_model)

    # -------------------------------------------------------------------------
    # Per-Detection Details Table
    # -------------------------------------------------------------------------
    if result is not None and result.boxes:
        st.markdown("### Per-Detection Details")

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
        if st.button("Prediction Correct", use_container_width=True, key="feedback_correct"):
            if annotated_image is not None and result is not None:
                save_feedback(annotated_image, result.boxes, selected_model, correct=True)
                st.success("Saved to failed_cases/ as a correct prediction.")
            else:
                st.warning("No detection result available to save.")

    with fb_col2:
        if st.button("Prediction Incorrect", use_container_width=True, key="feedback_incorrect"):
            if annotated_image is not None and result is not None:
                save_feedback(annotated_image, result.boxes, selected_model, correct=False)
                st.success("Saved to failed_cases/ for review.")
            else:
                st.warning("No detection result available to save.")
