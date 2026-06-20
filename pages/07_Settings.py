"""07_Settings.py — Platform configuration."""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.components.layout import inject_custom_css, page_header

# Page setup
inject_custom_css()
page_header("Settings", "Platform Configuration")

# Initialize settings
if "settings" not in st.session_state:
    st.session_state.settings = {"conf": 0.25, "iou": 0.45}

settings = st.session_state.settings

# --- Detection Parameters ---
st.markdown("### Detection Parameters")
cols = st.columns(2)
with cols[0]:
    new_conf = st.slider(
        "Confidence Threshold",
        0.0,
        1.0,
        float(settings.get("conf", 0.25)),
        0.01,
        help="Minimum confidence score for a detection to be valid",
    )
with cols[1]:
    new_iou = st.slider(
        "IoU Threshold",
        0.0,
        1.0,
        float(settings.get("iou", 0.45)),
        0.01,
        help="Intersection over Union threshold for non-maximum suppression",
    )

st.markdown("---")

# --- Save Button ---
if st.button("Save Settings", use_container_width=True):
    st.session_state.settings = {
        "conf": new_conf,
        "iou": new_iou,
    }
    # Update any cached engines with new thresholds
    for key in list(st.session_state.keys()):
        if key.startswith("engine_"):
            engine = st.session_state[key]
            engine.conf = new_conf
            engine.iou = new_iou
    st.success("Settings saved and applied.")

# --- Current Settings Summary ---
st.markdown("### Current Settings")
summary_cols = st.columns(3)
with summary_cols[0]:
    st.metric("Confidence", f"{settings.get('conf', 0.25):.0%}")
with summary_cols[1]:
    st.metric("IoU", f"{settings.get('iou', 0.45):.0%}")
with summary_cols[2]:
    active = st.session_state.get("active_model", "None")
    st.metric("Active Model", active)
