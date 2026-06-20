"""04_AI_Command_Center.py — AI Command Center with real system data."""
import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.components.layout import inject_custom_css, page_header
from src.components.cards import metric_card, info_card, status_card
from src.components.charts import gauge_chart, bar_chart, line_chart
from src.utils.system import cpu_percent, ram_info, gpu_info

# Page setup
inject_custom_css()
page_header("AI Command Center", "Executive Dashboard")

# Ensure tracker exists
if "tracker" not in st.session_state:
    st.info("No detections yet. Use the Detection Studio to start analyzing images.")
    st.stop()

tracker = st.session_state.tracker
summary = tracker.summary()
records = tracker.recent(20)

# Get real system metrics
cpu_val = cpu_percent()
ram_val = ram_info()
gpus = gpu_info()

# ============================================================
# Top KPI Row (4 columns)
# ============================================================
cols = st.columns(4)
with cols[0]:
    metric_card("Total Inferences", f"{summary['count']}")
with cols[1]:
    avg_ms = summary.get("avg_ms", 0)
    metric_card("Avg Inference", f"{avg_ms:.1f} ms")
with cols[2]:
    active_model = st.session_state.get("active_model", "None")
    metric_card("Active Model", active_model)
with cols[3]:
    fps = summary.get("fps", 0)
    metric_card("FPS", f"{fps:.1f}")

st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

# ============================================================
# Second Row (2 columns): System Status + Detection Health
# ============================================================
cols = st.columns(2)

with cols[0]:
    # System Status card with real CPU and RAM gauges
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#e2e8f0; font-size:1rem; font-weight:600; margin-bottom:16px;'>System Status</h3>", unsafe_allow_html=True)
    
    sys_cols = st.columns(2)
    with sys_cols[0]:
        gauge_chart(cpu_val, "CPU Usage", 100, 70)
    with sys_cols[1]:
        gauge_chart(ram_val["percent"], "RAM Usage", 100, 70)
    
    # Show GPU info if available
    if gpus:
        st.markdown("<h4 style='color:#e2e8f0; font-size:0.9rem; margin-top:16px; margin-bottom:8px;'>GPU</h4>", unsafe_allow_html=True)
        for gpu in gpus:
            gpu_util = gpu.get("utilization", 0)
            gauge_chart(gpu_util, f"{gpu.get('name', 'GPU')}", 100, 70)
    
    st.markdown("</div>", unsafe_allow_html=True)

with cols[1]:
    # Detection Health card with real threshold settings
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#e2e8f0; font-size:1rem; font-weight:600; margin-bottom:16px;'>Detection Health</h3>", unsafe_allow_html=True)
    
    settings = st.session_state.get("settings", {})
    conf_threshold = settings.get("conf", 0.25)
    iou_threshold = settings.get("iou", 0.45)
    
    info_items = [
        {"label": "Confidence Threshold", "value": f"{conf_threshold:.2f}"},
        {"label": "IoU Threshold", "value": f"{iou_threshold:.2f}"},
        {"label": "RAM Usage", "value": f"{ram_val['used_gb']:.1f} / {ram_val['total_gb']:.1f} GB"},
        {"label": "CPU Load", "value": f"{cpu_val:.1f}%"},
    ]
    
    for item in info_items:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.06);">
            <span style="color:#94a3b8; font-size:0.9rem;">{item['label']}</span>
            <span style="color:#00d4aa; font-weight:600; font-size:0.9rem;">{item['value']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

# ============================================================
# Recent Activity
# ============================================================
st.markdown("<h3 style='color:#e2e8f0; font-size:1.1rem; font-weight:600; margin-bottom:16px; letter-spacing:0.05em; text-transform:uppercase;'>Recent Activity</h3>", unsafe_allow_html=True)

if summary["count"] == 0:
    st.info("No detections yet. Use the Detection Studio to start analyzing images.")
else:
    recent_records = tracker.recent(10)
    if recent_records:
        df = pd.DataFrame(recent_records)
        df.columns = ["Inference (ms)", "Model", "Detections"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent inference records available.")

st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

# ============================================================
# Model Performance (bar chart if records exist)
# ============================================================
if records:
    # Aggregate detections per model
    model_stats = {}
    for record in records:
        model = record.get("model", "Unknown")
        detections = record.get("detections", 0)
        if model in model_stats:
            model_stats[model] += detections
        else:
            model_stats[model] = detections
    
    if model_stats:
        st.markdown("<h3 style='color:#e2e8f0; font-size:1.1rem; font-weight:600; margin-bottom:16px; letter-spacing:0.05em; text-transform:uppercase;'>Model Performance</h3>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        
        perf_df = pd.DataFrame({
            "Model": list(model_stats.keys()),
            "Total Detections": list(model_stats.values()),
        })
        bar_chart(perf_df, "Model", "Total Detections", "Detections by Model")
        
        st.markdown("</div>", unsafe_allow_html=True)