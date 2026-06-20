import os
import sys
import tempfile
from typing import List, Dict, Any

import streamlit as st
import pandas as pd
import numpy as np
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.components.layout import inject_custom_css, page_header
from src.components.charts import bar_chart
from src.core.engine import YOLOEngine


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scan_models() -> list[str]:
    root = get_project_root()
    return sorted([f for f in os.listdir(root) if f.endswith(".pt")])


def process_video(
    video_path: str,
    engine: YOLOEngine,
    sample_rate: int,
    progress_bar,
    status_text,
):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    results = []
    key_frames = []
    frame_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_rate == 0:
                res = engine.predict_frame(frame)
                results.append({
                    "frame_idx": frame_idx,
                    "detections": len(res.boxes),
                    "class_counts": res.class_counts,
                    "inference_ms": res.inference_ms,
                    "boxes": res.boxes,
                })
                if res.annotated_image is not None and frame_idx % (sample_rate * 5) == 0:
                    key_frames.append(res.annotated_image)

                if "tracker" in st.session_state and st.session_state.tracker is not None:
                    st.session_state.tracker.record(
                        res.inference_ms,
                        st.session_state.active_model,
                        len(res.boxes),
                    )

            pct = int(100 * frame_idx / total_frames) if total_frames > 0 else 0
            progress_bar.progress(min(pct / 100, 1.0))
            status_text.text(f"Processing frame {frame_idx} / {total_frames}")
            frame_idx += 1
    finally:
        cap.release()

    return results, key_frames, total_frames


def main():
    inject_custom_css()
    page_header("Video Intelligence", "Frame-by-frame video analysis")

    st.session_state.setdefault("video_results", None)
    st.session_state.setdefault("video_key_frames", None)
    st.session_state.setdefault("video_total_frames", None)

    # Controls row
    col1, col2, col3, col4 = st.columns(4)

    available_models = scan_models()
    default_model = available_models[0] if available_models else None

    with col1:
        model_file = st.selectbox(
            "Model",
            options=available_models,
            index=0 if available_models else 0,
        )

    with col2:
        confidence = st.slider(
            "Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
        )

    with col3:
        sample_rate = st.slider(
            "Sample Rate",
            min_value=1,
            max_value=30,
            value=5,
            step=1,
        )

    with col4:
        uploaded_file = st.file_uploader(
            "Video File",
            type=["mp4", "avi", "mov"],
        )

    st.divider()

    analyze_clicked = st.button("Analyze Video", type="primary", use_container_width=True)

    progress_bar = st.progress(0.0)
    status_text = st.empty()

    if analyze_clicked and uploaded_file is not None:
        status_text.text("Loading video...")
        progress_bar.progress(0.0)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            engine = YOLOEngine(model_file, confidence=confidence)
            st.session_state.active_model = model_file
            status_text.text("Processing video...")
            results, key_frames, total_frames = process_video(
                tmp_path, engine, sample_rate, progress_bar, status_text
            )

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
    elif analyze_clicked and uploaded_file is None:
        st.warning("Please upload a video file before analyzing.")

    if st.session_state.video_results is None:
        st.info("Upload a video file and click 'Analyze Video' to begin.")
        return

    results = st.session_state.video_results
    key_frames = st.session_state.video_key_frames or []
    total_frames = st.session_state.video_total_frames or 0

    # Metrics row
    total_detections = sum(r["detections"] for r in results)
    avg_detections = total_detections / len(results) if results else 0

    all_class_counts: Dict[str, int] = {}
    for r in results:
        for cls, cnt in r.get("class_counts", {}).items():
            all_class_counts[cls] = all_class_counts.get(cls, 0) + cnt

    most_frequent_class = max(all_class_counts, key=all_class_counts.get) if all_class_counts else "N/A"

    total_processing_ms = sum(r.get("inference_ms", 0) for r in results)
    total_processing_sec = total_processing_ms / 1000

    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    m_col1.metric("Total Frames", f"{len(results)}")
    m_col2.metric("Total Detections", f"{total_detections}")
    m_col3.metric("Avg Detections/Frame", f"{avg_detections:.2f}")
    m_col4.metric("Most Frequent Class", most_frequent_class)
    m_col5.metric("Total Processing Time", f"{total_processing_sec:.2f}s")

    st.divider()

    # Key frames gallery
    if key_frames:
        st.subheader("Key Frames")
        for i in range(0, len(key_frames), 3):
            row_frames = key_frames[i : i + 3]
            cols = st.columns(len(row_frames))
            for j, frame in enumerate(row_frames):
                with cols[j]:
                    st.image(frame, channels="BGR")
        st.divider()

    # Detection timeline
    if results:
        timeline_df = pd.DataFrame({
            "Frame": [r["frame_idx"] for r in results],
            "Detections": [r["detections"] for r in results],
        })
        bar_chart(timeline_df, x="Frame", y="Detections", title="Detections per Frame")

    # Frame summary dataframe
    if results:
        st.subheader("Frame Summary")
        summary_rows = []
        for r in results:
            row = {
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