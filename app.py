import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
import cv2
import tempfile
from collections import Counter
import os

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Road Marking Detection",
    page_icon="🚗",
    layout="wide"
)

# =========================================================
# HEADER
# =========================================================
st.title("🚗 AI Road Marking Detection Platform")
st.markdown("### Detect road markings and road damage using YOLO models")
st.info("📌 Upload only road-related images or videos you want to analyze.")
st.markdown("---")

# =========================================================
# ABOUT SECTION
# =========================================================
st.subheader("📑 About the App")
st.markdown("""
This platform uses multiple YOLO models for different detection tasks:

- **YOLOv8 / YOLOv11 → Road Marking Detection**  
  Classes: Lane lines, zebra crossings, stop lines, arrows, and other painted road markings.  

- **YOLOv8_RDD (Cracks & Potholes)**  
  Classes: Longitudinal cracks, Transverse cracks, Alligator cracks, Block cracks, Sealed cracks, and Potholes.  

Together, these models help identify missing or degraded markings and also detect cracks/potholes to improve road safety.
""")
st.markdown("---")

# =========================================================
# MODEL SELECTION + UPLOAD
# =========================================================
st.subheader("⚙️ Select Model & Mode")
col1, col2 = st.columns(2)

model_map = {
    "yolov8.pt": "YOLOv8 (Road Markings)",
    "yolov11.pt": "YOLOv11 (Road Markings)",
    "yolov8_RDD_cracks.pt": "YOLOv8_RDD (Cracks & Potholes)"
}

available_models = [f for f in model_map.keys() if os.path.exists(f)]
selected_file = st.selectbox("Choose YOLO Model:", available_models, format_func=lambda x: model_map[x])

with col2:
    mode = st.radio("Detection Mode:", ["Image", "Video"])

uploaded_file = st.file_uploader(
    "📤 Upload Image/Video", 
    type=["jpg","jpeg","png","mp4","avi","mov"]
)

MODEL_PATH = selected_file
if not os.path.exists(MODEL_PATH):
    st.error(f"{MODEL_PATH} not found in project folder")
    st.stop()

model = YOLO(MODEL_PATH)
st.success(f"✅ Model Loaded: {model_map[MODEL_PATH]}")

# =========================================================
# IMAGE DETECTION
# =========================================================
if mode == "Image" and uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)

    with st.spinner("Running Detection..."):
        results = model.predict(image_np, conf=0.25)

    annotated = results[0].plot()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(image, width="stretch")
    with col2:
        st.subheader("Detection Output")
        st.image(annotated, channels="BGR", width="stretch")

    boxes = results[0].boxes
    detected_classes = [model.names[int(box.cls[0])] for box in boxes]
    counts = Counter(detected_classes)

    st.subheader("🧠 Detection Summary")
    if counts:
        df = pd.DataFrame({"Class": list(counts.keys()), "Count": list(counts.values())})
        st.dataframe(df, width="stretch")
    else:
        st.warning("No objects detected.")

    failed_dir = "failed_cases"
    os.makedirs(failed_dir, exist_ok=True)

    fb_col1, fb_col2 = st.columns(2)
    with fb_col1:
        if st.button("✅ Predicted Correctly"):
            st.success("Thanks for confirming! Logged as correct.")

    with fb_col2:
        if st.button("❌ Not Predicted"):
            save_path = os.path.join(failed_dir, uploaded_file.name)
            image.save(save_path)
            st.error(f"Image saved to {save_path} for review.")

# =========================================================
# VIDEO DETECTION
# =========================================================
elif mode == "Video" and uploaded_file:
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_file.read())
    temp_file.close()   # ✅ close before using

    cap = cv2.VideoCapture(temp_file.name)
    stframe = st.empty()

    detected_classes = []
    frame_count = 0

    with st.spinner("Processing Video..."):
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            results = model.predict(frame, conf=0.25)
            boxes = results[0].boxes
            detected_classes.extend([model.names[int(box.cls[0])] for box in boxes])

            annotated_frame = results[0].plot()
            stframe.image(annotated_frame, channels="BGR", width="stretch")

    cap.release()
    os.remove(temp_file.name)   # ✅ safe delete

    counts = Counter(detected_classes)

    st.subheader("🎥 Video Analysis Summary")
    st.write(f"**Frames Processed:** {frame_count}")
    if counts:
        df = pd.DataFrame({"Class": list(counts.keys()), "Count": list(counts.values())})
        st.dataframe(df, width="stretch")
    else:
        st.warning("No objects detected.")

    failed_dir = "failed_cases"
    os.makedirs(failed_dir, exist_ok=True)

    fb_col1, fb_col2 = st.columns(2)
    with fb_col1:
        if st.button("✅ Predicted Correctly"):
            st.success("Thanks for confirming! Logged as correct.")

    with fb_col2:
        if st.button("❌ Not Predicted"):
            save_path = os.path.join(failed_dir, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.error(f"Video saved to {save_path} for review.")

# =========================================================
# FOOTER NOTE
# =========================================================
st.markdown("---")
st.caption("Developed by Vamshi Krishna Macha | Powered by YOLO & Streamlit")
