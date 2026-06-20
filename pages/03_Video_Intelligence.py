"""Video Intelligence — real-time streaming video analysis with YOLO."""
import os
import sys
import tempfile
import time
from collections import defaultdict
from typing import List, Dict, Any

import streamlit as st
import pandas as pd
import numpy as np
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.components.layout import inject_custom_css, page_header
from src.components.cards import metric_card
from src.components.charts import bar_chart
from src.core.engine import YOLOEngine
from src.utils.exporters import export_detections_json, export_detections_csv, export_image_bytes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scan_models() -> list[str]:
    root = get_project_root()
    return sorted([f for f in os.listdir(root) if f.endswith(".pt")])


def get_model_path(name: str) -> str:
    return os.path.join(get_project_root(), name)


def aggregate_detections(results: list[dict]) -> tuple[int, dict]:
    total = sum(r["detections"] for r in results)
    class_counts: Dict[str, int] = defaultdict(int)
    for r in results:
        for cls, cnt in r.get("class_counts", {}).items():
            class_counts[cls] += cnt
    return total, dict(class_counts)


def compute_fps(inference_times: list[float]) -> float:
    if not inference_times:
        return 0.0
    avg = sum(inference_times) / len(inference_times)
    return round(1000.0 / avg, 1) if avg > 0 else 0.0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    inject_custom_css()
    page_header("Video Intelligence", "Frame-by-frame video analysis")

    # Session state defaults
    st.session_state.setdefault("video_results", None)
    st.session_state.setdefault("video_key_frames", None)
    st.session_state.setdefault("video_total_frames", None)
    st.session_state.setdefault("video_source_fps", 0.0)

    available_models = scan_models()
    if not available_models:
        st.error("No .pt model files found in the project root. Please add a YOLO model.")
        return

    if "active_model" not in st.session_state or st.session_state.active_model not in available_models:
        st.session_state.active_model = available_models[0]

    settings = st.session_state.get("settings", {"conf": 0.25, "iou": 0.45})

    # -----------------------------------------------------------------------
    # Controls row
    # -----------------------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        selected_model = st.selectbox(
            "Model",
            options=available_models,
            index=available_models.index(st.session_state.active_model),
        )

    with c2:
        confidence = st.slider(
            "Confidence",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=settings.get("conf", 0.25),
        )

    with c3:
        sample_rate = st.slider(
            "Sample Rate",
            min_value=1,
            max_value=30,
            step=1,
            value=5,
        )

    with c4:
        uploaded_video = st.file_uploader(
            "Video File",
            type=["mp4", "avi", "mov"],
        )

    st.divider()

    start_processing = st.button(
        "Start Processing",
        type="primary",
        use_container_width=True,
    )

    # -----------------------------------------------------------------------
    # Processing
    # -----------------------------------------------------------------------
    if start_processing and uploaded_video is not None:
        settings["conf"] = confidence
        st.session_state.settings = settings
        st.session_state.active_model = selected_model

        # Unique key for this processing run
        proc_key = f"proc_{uploaded_video.name}_{selected_model}_{confidence}_{sample_rate}"

        # Save uploaded file to temp
        suffix = os.path.splitext(uploaded_video.name)[1] or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_video.getvalue())
            tmp_path = tmp.name

        # Live placeholders
        live_preview = st.empty()
        stats_placeholder = st.empty()
        progress_bar = st.progress(0.0)
        status_text = st.empty()

        try:
            status_text.text("Loading model...")
            engine = YOLOEngine(get_model_path(selected_model), conf=confidence)

            cap = cv2.VideoCapture(tmp_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps_source = cap.get(cv2.CAP_PROP_FPS)
            st.session_state.video_source_fps = fps_source

            results: list[dict] = []
            key_frames: list[np.ndarray] = []
            inference_times: list[float] = []
            frame_idx = 0
            processed_count = 0
            preview_update_rate = 15
            start_time = time.perf_counter()

            status_text.text("Processing video...")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % sample_rate == 0:
                    res = engine.predict_frame(frame)
                    inference_times.append(res.inference_ms)
                    results.append({
                        "frame_idx": frame_idx,
                        "detections": len(res.boxes),
                        "class_counts": dict(res.class_counts),
                        "inference_ms": res.inference_ms,
                        "boxes": res.boxes,
                        "model": selected_model,
                    })
                    if res.annotated_image is not None and processed_count % preview_update_rate == 0:
                        key_frames.append(res.annotated_image)

                    processed_count += 1

                    # Rolling averages
                    avg_ms = sum(inference_times) / len(inference_times)
                    fps = round(1000.0 / avg_ms, 1) if avg_ms > 0 else 0.0
                    pct = frame_idx / total_frames if total_frames > 0 else 0.0

                    # Live preview
                    if res.annotated_image is not None:
                        live_preview.image(
                            res.annotated_image,
                            channels="BGR",
                            use_container_width=True,
                            caption=f"Frame {frame_idx} | {len(res.boxes)} detections",
                        )

                    # Live stats row
                    with stats_placeholder.container():
                        sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
                        with sc1:
                            st.metric("Frame", frame_idx)
                        with sc2:
                            st.metric("Detections", len(res.boxes))
                        with sc3:
                            st.metric("FPS", f"{fps:.1f}")
                        with sc4:
                            st.metric("Avg Inference", f"{avg_ms:.1f} ms")
                        with sc5:
                            st.metric("Model", selected_model)
                        with sc6:
                            st.metric("Progress", f"{pct:.0%}")

                    # Progress bar
                    progress_bar.progress(min(pct, 1.0))
                    status_text.text(f"Processing frame {frame_idx} / {total_frames}")

                frame_idx += 1

            cap.release()

            # Store results
            st.session_state.video_results = results
            st.session_state.video_key_frames = key_frames
            st.session_state.video_total_frames = total_frames

            status_text.text("Processing complete!")
            progress_bar.progress(1.0)

        except Exception as e:
            status_text.text(f"Error: {str(e)}")
            st.error(f"Video processing failed: {str(e)}")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    elif start_processing and uploaded_video is None:
        st.warning("Please upload a video file before starting processing.")

    # -----------------------------------------------------------------------
    # Post-processing analytics dashboard
    # -----------------------------------------------------------------------
    if st.session_state.video_results is None:
        st.info("Upload a video file and click **Start Processing** to begin analysis.")
        return

    results = st.session_state.video_results
    key_frames = st.session_state.video_key_frames or []
    total_frames = st.session_state.video_total_frames or 0
    fps_source = st.session_state.video_source_fps or 0.0

    if not results:
        st.warning("No frames were processed. Try adjusting the sample rate or confidence.")
        return

    # KPIs
    total_detections, class_counts = aggregate_detections(results)
    sampled_count = len(results)
    avg_detections = total_detections / sampled_count if sampled_count else 0
    inference_times = [r["inference_ms"] for r in results]
    avg_inference = sum(inference_times) / len(inference_times) if inference_times else 0.0
    fps_processed = compute_fps(inference_times)
    top_class = max(class_counts, key=class_counts.get) if class_counts else "N/A"
    active_model = results[0].get("model", "N/A") if results else "N/A"

    st.divider()

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    kpi1.metric("Total Frames", total_frames)
    kpi2.metric("Sampled Frames", sampled_count)
    kpi3.metric("Total Detections", total_detections)
    kpi4.metric("Avg Detections/Frame", f"{avg_detections:.1f}")
    kpi5.metric("Avg Inference", f"{avg_inference:.1f} ms")
    kpi6.metric("FPS", f"{fps_processed:.1f}")

    st.divider()

    # Top class and model info
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        metric_card("Top Detected Class", top_class)
    with info_col2:
        metric_card("Active Model", active_model)

    st.divider()

    # Detection timeline
    timeline_df = pd.DataFrame({
        "Frame": [r["frame_idx"] for r in results],
        "Detections": [r["detections"] for r in results],
    })
    bar_chart(timeline_df, x="Frame", y="Detections", title="Detections per Frame")

    # Class distribution
    if class_counts:
        class_df = pd.DataFrame({
            "Class": list(class_counts.keys()),
            "Count": list(class_counts.values()),
        }).sort_values("Count", ascending=False)
        bar_chart(class_df, x="Class", y="Count", title="Detection Count by Class")

    st.divider()

    # Key frames gallery
    if key_frames:
        st.subheader("Key Frames Gallery")
        for i in range(0, len(key_frames), 3):
            row_frames = key_frames[i : i + 3]
            img_cols = st.columns(len(row_frames))
            for j, frame_img in enumerate(row_frames):
                with img_cols[j]:
                    st.image(frame_img, channels="BGR", use_container_width=True)

    st.divider()

    # Export row
    st.subheader("Export Results")
    export_col1, export_col2, export_col3 = st.columns(3)

    all_boxes = [box for r in results for box in r.get("boxes", [])]
    json_data = export_detections_json(all_boxes)
    csv_data = export_detections_csv(all_boxes)

    with export_col1:
        st.download_button(
            "Download JSON",
            data=json_data,
            file_name="detections.json",
            mime="application/json",
            use_container_width=True,
        )

    with export_col2:
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name="detections.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with export_col3:
        if key_frames:
            first_key_frame = key_frames[0]
            png_bytes = export_image_bytes(first_key_frame)
            st.download_button(
                "Download Key Frame (PNG)",
                data=png_bytes,
                file_name="key_frame.png",
                mime="image/png",
                use_container_width=True,
            )

    st.divider()

    # Frame summary table
    st.subheader("Frame Summary")
    summary_rows = []
    for r in results:
        row: Dict[str, Any] = {
            "Frame": r["frame_idx"],
            "Detections": r["detections"],
            "Inference (ms)": round(r.get("inference_ms", 0), 2),
        }
        for cls, cnt in r.get("class_counts", {}).items():
            row[cls] = cnt
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()