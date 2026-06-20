"""Road Safety Intelligence Platform — Landing Page."""
import os
import sys
from collections import deque

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.components.layout import inject_custom_css, hero_section
from src.utils.system import cpu_percent
from src.utils.hf_hub import ensure_models


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Road Safety Intelligence Platform",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar chrome
# ---------------------------------------------------------------------------
st.sidebar.markdown(
    """
    <h1 style='text-align:center; margin-bottom:30px; font-size:1.5rem; font-weight:700;
               background:linear-gradient(90deg,#00d4aa,#7c3aed);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
        ROAD SAFETY INTELLIGENCE
    </h1>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    """
    <p style='text-align:center; color:#64748b; font-size:0.75rem;
              letter-spacing:0.15em; text-transform:uppercase; margin-bottom:30px;'>
        Infrastructure Intelligence
    </p>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("<hr style='margin-bottom:30px;'>", unsafe_allow_html=True)

# Suppress Streamlit chrome
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"]::before { content: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="stSidebarNavFooter"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def scan_models() -> list[str]:
    """Dynamically discover .pt model files in the project root."""
    root = os.path.dirname(os.path.abspath(__file__))
    return sorted([f for f in os.listdir(root) if f.endswith(".pt")])


def _js_counter(label: str, target: int, suffix: str = "", duration: int = 2000, uid: str = "c0") -> str:
    """Return a small HTML/JS animated counter for use inside components.html."""
    suffix_html = (
        f"<div style='font-size:0.9rem; color:#64748b; margin-top:4px;'>{suffix}</div>"
        if suffix
        else ""
    )
    return f"""
    <div style="text-align:center; padding:24px 16px;
                background:rgba(20,25,40,0.5); border:1px solid rgba(255,255,255,0.06);
                border-radius:16px;">
        <div style="color:#94a3b8; font-size:0.75rem; text-transform:uppercase;
                    letter-spacing:0.12em; margin-bottom:12px;">
            {label}
        </div>
        <div id="counter_{uid}" style="font-size:2.5rem; font-weight:700; color:#00d4aa;">
            0
        </div>
        {suffix_html}
    </div>
    <script>
        (function() {{
            const target = {target};
            const duration = {duration};
            const el = document.getElementById('counter_{uid}');
            if (!el) return;
            const start = performance.now();
            function update(now) {{
                const elapsed = now - start;
                const progress = Math.min(elapsed / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                el.textContent = Math.floor(target * eased).toLocaleString();
                if (progress < 1) requestAnimationFrame(update);
            }}
            requestAnimationFrame(update);
        }})();
    </script>
    """


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "tracker" not in st.session_state:
    from src.core.tracker import InferenceTracker

    st.session_state.tracker = InferenceTracker()

if "active_model" not in st.session_state:
    ensure_models()
    model_files = scan_models()
    st.session_state.active_model = model_files[0] if model_files else "yolov8.pt"

if "settings" not in st.session_state:
    st.session_state.settings = {"conf": 0.25, "iou": 0.45}

# ---------------------------------------------------------------------------
# CSS injection FIRST (after layout session state to avoid reimport issues)
# ---------------------------------------------------------------------------
inject_custom_css()

# ---------------------------------------------------------------------------
# 1. HERO SECTION
# ---------------------------------------------------------------------------
hero_section("ROAD SAFETY INTELLIGENCE PLATFORM", "AI-Powered Infrastructure Monitoring & Defect Detection")

st.markdown(
    """
    <div style="text-align:center; margin-top:-10px; margin-bottom:20px;">
        <p style="color:#94a3b8; font-size:0.95rem; margin-bottom:4px;">
            Developed by <strong style="color:#e2e8f0;">Vamshi Krishna Macha</strong>
        </p>
        <p style="color:#64748b; font-size:0.75rem; letter-spacing:0.08em;">
            AI Research  |  Computer Vision  |  Infrastructure Intelligence
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# DEPLOYMENT READY — Featured: iOS + Android
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:40px 0 10px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='text-align:center; color:#e2e8f0; font-size:1.4rem; font-weight:600; margin-bottom:8px;'"
    ">Deployment Ready</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#94a3b8; font-size:0.85rem; margin-bottom:24px;'>"
    "Built for modern infrastructure — deploy anywhere, scale everywhere."
    "</p>",
    unsafe_allow_html=True,
)

IOS_ICON = (
    '<svg viewBox="0 0 24 24" width="80" height="80" fill="#e2e8f0">'
    '<path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.67-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.58-.72 1.37-1.16 2.26-1.18.1 1.05-.29 2.09-.92 2.87-.65.77-1.51 1.22-2.42 1.2-.12-1.05.36-2.11 1.08-2.89z"/>'
    "</svg>"
)
ANDROID_ICON = (
    '<svg viewBox="0 0 24 24" width="80" height="80" fill="#3ddc84">'
    '<path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1529-.5676.416.416 0 00-.5676.1529l-2.0225 3.502C15.5902 8.4792 13.8539 8.1772 12 8.1772c-1.8539 0-3.5902.302-5.1357.8452L4.8418 5.5204a.415.415 0 00-.5676-.1529.415.415 0 00-.1529.5676l1.9973 3.4592C2.6889 11.1867.3432 14.6589.3432 18.6617h23.3136c0-4.0028-2.3457-7.475-5.7755-9.3403"/>'
    "</svg>"
)

featured = [
    (IOS_ICON, "iOS", "Native Mobile Application", "Future Production Deployment", "#f59e0b", "rgba(0,212,170,0.25)"),
    (ANDROID_ICON, "Android", "Mobile Edge AI", "Real-Time Detection", "#f59e0b", "rgba(61,220,132,0.25)"),
]

f1, f2, f3 = st.columns([1, 3.5, 1])
with f2:
    fc1, fc2 = st.columns(2)
    for col, (icon, name, tag, desc, badge_color, border_color) in zip([fc1, fc2], featured):
        with col:
            st.markdown(
                f"""
                <div class="platform-card priority" style="text-align:center; padding:28px 16px;
                         background:rgba(20,25,40,0.6); border:1px solid {border_color};
                         border-radius:16px; height:100%;">
                    <div style="margin-bottom:14px; display:flex; justify-content:center; align-items:center; min-height:84px;">
                        {icon}
                    </div>
                    <div style="color:#e2e8f0; font-size:1.1rem; font-weight:700; margin-bottom:6px;">
                        {name}
                    </div>
                    <div style="color:#94a3b8; font-size:0.85rem; margin-bottom:6px;">
                        {tag}
                    </div>
                    <div style="color:#64748b; font-size:0.75rem; margin-bottom:10px;">
                        {desc}
                    </div>
                    <div style="display:inline-block; background:{badge_color}; color:#0a0e17;
                                font-size:0.7rem; font-weight:700; padding:3px 12px;
                                border-radius:999px;">
                        ✓ Planned
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------------
# 2. OVERVIEW CARDS (4 columns)
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:30px 0 10px;'></div>", unsafe_allow_html=True)

overview_items = [
    (
        "🔍",
        "Real-Time Detection",
        "AI-powered road marking detection with sub-50ms inference",
    ),
    (
        "🎬",
        "Video Intelligence",
        "Frame-by-frame video analysis with live preview and export",
    ),
    (
        "🧠",
        "Multi-Model Support",
        "Seamless switching between YOLOv8, YOLOv9, and custom models",
    ),
    (
        "📊",
        "Infrastructure Analytics",
        "System health, inference tracking, and performance dashboards",
    ),
]

ov_cols = st.columns(4)
for idx, (icon, title, desc) in enumerate(overview_items):
    with ov_cols[idx]:
        st.markdown(
            f"""
            <div class="overview-card" style="text-align:center; padding:24px 16px;
                     background:rgba(20,25,40,0.4); border:1px solid rgba(255,255,255,0.06);
                     border-radius:16px; height:100%;">
                <div style="font-size:48px; margin-bottom:12px;">{icon}</div>
                <div style="color:#e2e8f0; font-size:1rem; font-weight:600; margin-bottom:8px;">
                    {title}
                </div>
                <div style="color:#94a3b8; font-size:0.8rem; line-height:1.4;">
                    {desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# 3. STATISTICS ROW (animated JS counters)
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:30px 0 10px;'></div>", unsafe_allow_html=True)

tracker = st.session_state.tracker
summary = tracker.summary()

images_processed = summary.get("count", 0)

try:
    detect_counts = getattr(tracker, "_detect_counts", deque())
    total_detections = sum(detect_counts)
except Exception:
    total_detections = 0

models_available = len(scan_models())

system_health = round(max(0, min(100, 100 - cpu_percent())))

c1, c2, c3, c4 = st.columns(4)
with c1:
    components.html(_js_counter("Images Processed", images_processed, uid="c1"), height=140)
with c2:
    components.html(_js_counter("Detections Performed", total_detections, uid="c2"), height=140)
with c3:
    components.html(_js_counter("Models Available", models_available, uid="c3"), height=140)
with c4:
    suffix = "operational" if system_health >= 80 else "degraded" if system_health >= 50 else "critical"
    components.html(
        _js_counter("System Health", system_health, suffix=suffix, uid="c4"),
        height=140,
    )

# ---------------------------------------------------------------------------
# 4. SYSTEM STATUS PANEL (4 columns)
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:30px 0 10px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='text-align:center; color:#e2e8f0; font-size:1.4rem; font-weight:600; margin-bottom:24px;'>"
    "System Status</h2>",
    unsafe_allow_html=True,
)

panel_cols = st.columns(4)
with panel_cols[0]:
    st.metric("Active Model", st.session_state.active_model)
with panel_cols[1]:
    st.metric("Models Available", len(scan_models()))
with panel_cols[2]:
    st.metric("Inference Engine", "YOLO / Ultralytics")
with panel_cols[3]:
    cpu_val = cpu_percent()
    delta_color = "normal" if cpu_val < 80 else "inverse"
    platform_status = f"{cpu_val:.0f}%"
    st.metric("Platform Status", platform_status, delta_color=delta_color)

# ---------------------------------------------------------------------------
# Available Infrastructure — Web / Docker / Cloud
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:40px 0 10px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='text-align:center; color:#e2e8f0; font-size:1.4rem; font-weight:600; margin-bottom:8px;'>"
    "Available Infrastructure</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#64748b; font-size:0.8rem; margin-bottom:16px;'>"
    "Currently Available &nbsp;·&nbsp; Enterprise Deployment"
    "</p>",
    unsafe_allow_html=True,
)

infra = [
    ("🌐", "Web", "Active", "#00d4aa"),
    ("🐳", "Docker", "Ready", "#00d4aa"),
    ("☁️", "Cloud", "Ready", "#00d4aa"),
]

i1, i2, i3, i4, i5 = st.columns([1, 1.2, 1.2, 1.2, 1])
for col, (icon, name, status, badge_color) in zip([i2, i3, i4], infra):
    with col:
        st.markdown(
            f"""
            <div class="platform-card" style="text-align:center; padding:16px 10px;
                     background:rgba(20,25,40,0.4); border:1px solid rgba(255,255,255,0.06);
                     border-radius:14px; height:100%;">
                <div style="font-size:2rem; margin-bottom:8px; line-height:1;">{icon}</div>
                <div style="color:#e2e8f0; font-size:0.85rem; font-weight:600; margin-bottom:6px;">
                    {name}
                </div>
                <div style="display:inline-block; background:{badge_color}; color:#0a0e17;
                            font-size:0.65rem; font-weight:700; padding:2px 8px;
                            border-radius:999px;">
                    ✓ {status}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# 6. SUPPORTED PLATFORMS (5 columns)
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:40px 0 10px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='text-align:center; color:#e2e8f0; font-size:1.3rem; font-weight:600; margin-bottom:8px;'>"
    "Supported Platforms</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#94a3b8; font-size:0.85rem; margin-bottom:24px;'>"
    "Seamless integration across every layer of your stack."
    "</p>",
    unsafe_allow_html=True,
)

supported = [
    ("🌐", "Web", "Browser-based inference", False, None),
    (IOS_ICON, "iOS", "Native mobile support", True, "rgba(0,212,170,0.2)"),
    (ANDROID_ICON, "Android", "Edge deployment ready", True, "rgba(61,220,132,0.2)"),
    ("🐳", "Docker", "Containerized for scale", False, None),
    ("☁️", "Cloud", "AWS / GCP / Azure", False, None),
]

sup_cols = st.columns(5)
for idx, (icon, name, tag, priority, border_color) in enumerate(supported):
    with sup_cols[idx]:
        border = f"1px solid {border_color}" if border_color else "1px solid rgba(255,255,255,0.06)"
        priority_cls = " priority" if priority else ""
        icon_display = (
            f'<div style="font-size:2.2rem; margin-bottom:10px;">{icon}</div>'
            if isinstance(icon, str) and not icon.startswith("<")
            else f'<div style="margin-bottom:10px; display:flex; justify-content:center; align-items:center; min-height:54px;">{icon}</div>'
        )
        st.markdown(
            f"""
            <div class="platform-card{priority_cls}" style="text-align:center; padding:20px;
                     background:rgba(20,25,40,0.4); border:{border};
                     border-radius:16px; height:100%;">
                {icon_display}
                <div style="color:#e2e8f0; font-size:0.9rem; font-weight:600; margin-bottom:4px;">
                    {name}
                </div>
                <div style="color:#64748b; font-size:0.75rem;">
                    {tag}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# 7. FEATURE GRID (6 cards)
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:40px 0 10px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='text-align:center; color:#e2e8f0; font-size:1.5rem; font-weight:600; margin-bottom:30px;'>"
    "Platform Capabilities</h2>",
    unsafe_allow_html=True,
)

feature_cols = st.columns(3)
features = [
    (
        "AI Detection",
        "Advanced YOLO-based object detection for road markings, cracks, and infrastructure defects with real-time inference.",
    ),
    (
        "Video Analytics",
        "Process video streams and recorded footage to extract actionable insights about road conditions and safety metrics.",
    ),
    (
        "Real-Time Processing",
        "Sub-50ms inference times with optimized models delivering instantaneous results for time-critical applications.",
    ),
    (
        "Model Management",
        "Seamlessly switch between multiple YOLO models. Compare results and track performance across different versions.",
    ),
    (
        "Safety Analytics",
        "Identify hazardous road conditions, deteriorating markings, and infrastructure issues before they cause accidents.",
    ),
    (
        "System Monitoring",
        "Track system health, model performance, and inference statistics in real-time with detailed dashboards.",
    ),
]

for idx, (title, desc) in enumerate(features):
    with feature_cols[idx % 3]:
        st.markdown(
            f"""
            <div class="glass-card" style="padding:22px; margin-bottom:16px;">
                <h3 style="color:#e2e8f0; font-size:1.05rem; margin-bottom:8px;">{title}</h3>
                <p style="color:#94a3b8; font-size:0.82rem; line-height:1.5;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# 8. FOOTER
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="height:2px; background:linear-gradient(90deg, transparent, #00d4aa, #7c3aed, transparent);
                margin:40px 0; border-radius:2px;">
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style="text-align:center; padding:30px 20px; color:#64748b; font-size:0.85rem;">
        <p>Powered by YOLO | Road Safety Intelligence Platform</p>
        <p style="margin-top:8px; font-size:0.75rem;">Built with Streamlit, Ultralytics, and OpenCV</p>
    </div>
    """,
    unsafe_allow_html=True,
)
