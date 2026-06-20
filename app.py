"""Road Safety Intelligence Platform — Entry Point."""
import os
import streamlit as st
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.components.layout import inject_custom_css, hero_section

# Page configuration
st.set_page_config(
    page_title="Road Safety Intelligence Platform",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS FIRST
inject_custom_css()

# Custom sidebar header
st.sidebar.markdown(
    "<h1 style='text-align:center; margin-bottom:30px; font-size:1.5rem; font-weight:700; background:linear-gradient(90deg,#00d4aa,#7c3aed); -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>ROAD MARKING AI</h1>",
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "<p style='text-align:center; color:#64748b; font-size:0.75rem; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:30px;'>Infrastructure Intelligence</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown("<hr style='margin-bottom:30px;'>", unsafe_allow_html=True)

# Hide default Streamlit elements via CSS
st.markdown("""
<style>
/* Hide the default "app" text from sidebar */
[data-testid="stSidebarNav"]::before {
    content: none !important;
}
/* Hide Streamlit branding */
.stDeployButton {
    display: none !important;
}
/* Hide "Manage app" */
[data-testid="stSidebarNavFooter"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "tracker" not in st.session_state:
    from src.core.tracker import InferenceTracker
    st.session_state.tracker = InferenceTracker()

if "active_model" not in st.session_state:
    import os
    model_files = sorted([f for f in os.listdir(os.path.dirname(os.path.abspath(__file__))) if f.endswith(".pt")])
    st.session_state.active_model = model_files[0] if model_files else "yolov8.pt"

if "settings" not in st.session_state:
    st.session_state.settings = {"conf": 0.25, "iou": 0.45}

# ---------------------------------------------------------------------------
# CINEMATIC LANDING PAGE
# ---------------------------------------------------------------------------


hero_section("ROAD MARKING AI", "Real-Time Infrastructure Intelligence")

# Animated metrics row
st.markdown("<div style='margin:40px 0;'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; padding:24px 16px;'><div style='color:#94a3b8; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:12px;'>AI Detection</div><div style='font-size:2.5rem; font-weight:700; color:#00d4aa;'>YOLO</div><div style='font-size:0.85rem; color:#64748b; margin-top:8px;'>Real-time inference</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; padding:24px 16px;'><div style='color:#94a3b8; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:12px;'>Video Analytics</div><div style='font-size:2.5rem; font-weight:700; color:#00d4aa;'>Frame-level</div><div style='font-size:0.85rem; color:#64748b; margin-top:8px;'>Batch processing</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; padding:24px 16px;'><div style='color:#94a3b8; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:12px;'>Model Support</div><div style='font-size:2.5rem; font-weight:700; color:#00d4aa;'>Multi-version</div><div style='font-size:0.85rem; color:#64748b; margin-top:8px;'>YOLOv5-v11</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Feature grid
st.markdown("---", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center; color:#e2e8f0; font-size:1.5rem; font-weight:600; margin:40px 0 30px;'>Platform Capabilities</h2>", unsafe_allow_html=True)

feature_cols = st.columns(3)

features = [
    ("AI Detection", "Advanced YOLO-based object detection for road markings, cracks, and infrastructure defects with real-time inference."),
    ("Video Analytics", "Process video streams and recorded footage to extract actionable insights about road conditions and safety metrics."),
    ("Real-Time Processing", "Sub-50ms inference times with optimized models delivering instantaneous results for time-critical applications."),
    ("Model Management", "Seamlessly switch between multiple YOLO models. Compare results and track performance across different versions."),
    ("Safety Analytics", "Identify hazardous road conditions, deteriorating markings, and infrastructure issues before they cause accidents."),
    ("System Monitoring", "Track system health, model performance, and inference statistics in real-time with detailed dashboards."),
]

for idx, (title, desc) in enumerate(features):
    with feature_cols[idx % 3]:
        st.markdown(f"""
        <div class="glass-card" style="padding:20px; margin-bottom:16px;">
            <h3 style="color:#e2e8f0; font-size:1.1rem; margin-bottom:8px;">{title}</h3>
            <p style="color:#94a3b8; font-size:0.85rem; line-height:1.5;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# Gradient divider
st.markdown("<div style='height:2px; background:linear-gradient(90deg, transparent, #00d4aa, #7c3aed, transparent); margin:40px 0; border-radius:2px;'></div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; padding:30px 20px; color:#64748b; font-size:0.85rem;">
    <p>Powered by YOLO | Road Safety Intelligence Platform</p>
    <p style="margin-top:8px; font-size:0.75rem;">Built with Streamlit, Ultralytics, and OpenCV</p>
</div>
""", unsafe_allow_html=True)