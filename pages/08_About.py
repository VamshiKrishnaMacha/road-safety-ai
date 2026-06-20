"""08_About.py — About page with technology stack."""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.components.layout import inject_custom_css, page_header

inject_custom_css()

page_header("About", "Road Safety Intelligence Platform")

st.markdown("""
<div style="max-width:800px; margin:0 auto 40px; text-align:center;">
    <p style="color:#e2e8f0; font-size:1.05rem; line-height:1.7;">
        Road Safety Intelligence is a production-grade platform for infrastructure analysis using
        state-of-the-art YOLO computer vision models. Detect road markings, surface defects,
        and safety-critical infrastructure elements in real-time.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### Platform Capabilities")
capabilities = [
    "Real-time road marking detection and classification",
    "Video stream processing with frame-by-frame analysis",
    "Multiple YOLO model support",
    "Automated reporting with JSON and CSV export",
    "System health monitoring",
    "Batch processing for large-scale surveys",
]

cap_cols = st.columns(2)
for idx, cap in enumerate(capabilities):
    with cap_cols[idx % 2]:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; padding:12px 16px; margin-bottom:12px; background:rgba(20,25,40,0.5); border:1px solid rgba(255,255,255,0.06); border-radius:12px;">
            <div style="width:8px; height:8px; border-radius:50%; background:linear-gradient(135deg,#00d4aa,#059669); flex-shrink:0;"></div>
            <span style="color:#e2e8f0; font-size:0.95rem;">{cap}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("### Technology Stack")
tech_stack = ["Python", "YOLO", "Streamlit", "OpenCV", "Plotly", "Docker"]
tech_cols = st.columns(len(tech_stack))
for idx, name in enumerate(tech_stack):
    with tech_cols[idx]:
        st.markdown(f"""
        <div style="text-align:center; padding:20px; background:rgba(20,25,40,0.5); border:1px solid rgba(255,255,255,0.06); border-radius:16px;">
            <div style="font-size:2rem; margin-bottom:8px; color:#00d4aa;">◆</div>
            <div style="color:#e2e8f0; font-weight:600; font-size:0.95rem;">{name}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:30px 20px; color:#64748b; font-size:0.85rem; margin-top:40px;">
    <p>Version 2.0 | Road Safety Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)
