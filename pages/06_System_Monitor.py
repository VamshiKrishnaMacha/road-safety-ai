"""06_System_Monitor.py — Live system monitoring dashboard."""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.components.layout import inject_custom_css, page_header
from src.components.cards import metric_card, status_card, info_card
from src.utils.system import cpu_percent, ram_info, gpu_info

# Page setup
inject_custom_css()
page_header("System Monitor", "Live Performance Metrics")

# Refresh button — no auto-refresh to avoid infinite reload loop
st.button("Refresh Metrics", use_container_width=True)

# Read system metrics
cpu_val = cpu_percent()
ram_val = ram_info()
gpus = gpu_info()

# Get tracker summary
tracker = st.session_state.get("tracker")
if tracker is None:
    tracker = None
else:
    summary = tracker.summary()

# KPI Row (4 columns)
cols = st.columns(4)

with cols[0]:
    metric_card("CPU Usage", f"{cpu_val:.1f}%")

with cols[1]:
    metric_card("RAM Usage", f"{ram_val['percent']:.1f}%")

with cols[2]:
    if tracker is not None:
        metric_card("Avg Inference", f"{summary['avg_ms']:.1f} ms")
    else:
        metric_card("Avg Inference", "—")

with cols[3]:
    if tracker is not None:
        metric_card("Inferences", f"{summary['count']}")
    else:
        metric_card("Inferences", "—")

# Charts Row (2 columns)
chart_cols = st.columns(2)

with chart_cols[0]:
    st.markdown("### CPU / RAM")
    st.markdown(f"**CPU:** {cpu_val:.1f}%")
    st.markdown(f"**RAM:** {ram_val['used_gb']:.1f} GB / {ram_val['total_gb']:.1f} GB ({ram_val['percent']:.1f}%)")

with chart_cols[1]:
    st.markdown("### Inference Summary")
    if tracker is not None:
        summary = tracker.summary()
        st.markdown(f"- **Count:** {summary['count']}")
        st.markdown(f"- **Avg:** {summary['avg_ms']:.1f} ms")
        st.markdown(f"- **Min:** {summary['min_ms']:.1f} ms")
        st.markdown(f"- **Max:** {summary['max_ms']:.1f} ms")
        st.markdown(f"- **FPS:** {summary['fps']:.1f}")
    else:
        st.info("No inference data available. Run detection first to collect metrics.")

# GPU Section
st.markdown("### GPU Metrics")

if gpus:
    gpu_cols = st.columns(len(gpus))
    for idx, gpu in enumerate(gpus):
        with gpu_cols[idx]:
            info_card(gpu.get("name", f"GPU {idx}"), [
                {"label": "Utilization", "value": f"{gpu.get('utilization', 0):.1f}%"},
                {"label": "Memory", "value": f"{gpu.get('memory_used_mb', 0):.0f} / {gpu.get('memory_total_mb', 0):.0f} MB"},
                {"label": "Temperature", "value": f"{gpu.get('temperature_c', 0):.0f} °C"},
                {"label": "Power Draw", "value": f"{gpu.get('power_draw', 0):.1f} W"},
            ])
else:
    st.info("No GPU detected on this system.")

# System Overview Row (3 columns)
st.markdown("### System Overview")

overview_cols = st.columns(3)

with overview_cols[0]:
    cpu_status = "Normal" if cpu_val < 80 else "High"
    cpu_color = "#00d4aa" if cpu_val < 80 else "#f59e0b"
    status_card("CPU", cpu_status, cpu_color)

with overview_cols[1]:
    ram_status = "Normal" if ram_val["percent"] < 80 else "High"
    ram_color = "#00d4aa" if ram_val["percent"] < 80 else "#f59e0b"
    status_card("RAM", ram_status, ram_color)

with overview_cols[2]:
    gpu_status = "Available" if gpus else "Not Detected"
    gpu_color = "#00d4aa" if gpus else "#f59e0b"
    status_card("GPU", gpu_status, gpu_color)