"""Road Safety Intelligence Platform — Entry Point."""
import os
from collections import deque

import streamlit as st
import streamlit.components.v1 as components
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.components.layout import inject_custom_css, hero_section
from src.utils.system import cpu_percent


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
        ROAD MARKING AI
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


def _js_counter(label: str, target: int, suffix: str = "", duration: int = 2000, uid: str = "c0"):
    """Return a small HTML/JS animated counter for use inside components.html."""
    suffix_html = f"<div style='font-size:0.9rem; color:#64748b; margin-top:4px;'>{suffix}</div>" if suffix else ""
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
# Session state (before any visible content)
# ---------------------------------------------------------------------------
if "tracker" not in st.session_state:
    from src.core.tracker import InferenceTracker

    st.session_state.tracker = InferenceTracker()

if "active_model" not in st.session_state:
    model_files = scan_models()
    st.session_state.active_model = model_files[0] if model_files else "yolov8.pt"

if "settings" not in st.session_state:
    st.session_state.settings = {"conf": 0.25, "iou": 0.45}

# ---------------------------------------------------------------------------
# CSS injection FIRST
# ---------------------------------------------------------------------------
inject_custom_css()

# ---------------------------------------------------------------------------
# 1. HERO SECTION
# ---------------------------------------------------------------------------
hero_section("ROAD MARKING AI", "Real-Time Infrastructure Intelligence")

# Personal branding
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

# --- Animated hero container (SVG layers + scan line + detection boxes) ---
components.html(
    """
    <div style="position:relative; width:100%; height:500px;
                overflow:hidden; border-radius:12px;">

        <!-- Layer 1: Perspective Road Grid -->
        <svg style="position:absolute; top:0; left:0; width:100%; height:100%;
                    opacity:0.15; pointer-events:none; z-index:1;">
            <line class="lane" x1="30%" y1="0" x2="45%" y2="100%" />
            <line class="lane" x1="70%" y1="0" x2="55%" y2="100%" />
            <line class="centerline" x1="50%" y1="0" x2="50%" y2="100%"
                  stroke-dasharray="20,30" />
            <line class="crossline" x1="0" y1="20%" x2="100%" y2="20%" />
            <line class="crossline" x1="0" y1="40%" x2="100%" y2="40%" />
            <line class="crossline" x1="0" y1="60%" x2="100%" y2="60%" />
            <line class="crossline" x1="0" y1="80%" x2="100%" y2="80%" />
            <style>
                .lane {
                    stroke: rgba(0,212,170,0.25);
                    stroke-width: 2;
                    animation: lane-flow 15s linear infinite;
                }
                .centerline {
                    stroke: rgba(0,212,170,0.35);
                    stroke-width: 2;
                    animation: lane-flow 8s linear infinite;
                }
                .crossline {
                    stroke: rgba(124,58,237,0.1);
                    stroke-width: 1;
                    animation: cross-flow 20s linear infinite;
                }
                @keyframes lane-flow {
                    0% { stroke-dashoffset: 0; }
                    100% { stroke-dashoffset: 200; }
                }
                @keyframes cross-flow {
                    0% { stroke-dashoffset: 0; opacity: 0.3; }
                    50% { opacity: 0.7; }
                    100% { stroke-dashoffset: 400; opacity: 0.3; }
                }
            </style>
        </svg>

        <!-- Layer 2: Floating AI Detection Boxes -->
        <div style="position:absolute; top:0; left:0; width:100%; height:100%;
                    pointer-events:none; z-index:2;">
            <style>
                .det-box {
                    position: absolute;
                    border: 1px solid rgba(0,212,170,0.2);
                    background: rgba(0,212,170,0.03);
                    animation: det-pulse 6s ease-in-out infinite;
                }
                @keyframes det-pulse {
                    0%, 100% { opacity: 0; transform: scale(0.8); }
                    20%      { opacity: 1; transform: scale(1); }
                    80%      { opacity: 1; transform: scale(1); }
                }
            </style>
            <div class="det-box" style="top:30%; left:20%; width:60px; height:40px;
                                          animation-delay:0s;"></div>
            <div class="det-box" style="top:50%; left:70%; width:45px; height:35px;
                                          animation-delay:2s;"></div>
            <div class="det-box" style="top:70%; left:40%; width:50px; height:50px;
                                          animation-delay:4s;"></div>
            <div class="det-box" style="top:25%; left:60%; width:35px; height:25px;
                                          animation-delay:1s;"></div>
            <div class="det-box" style="top:60%; left:15%; width:55px; height:30px;
                                          animation-delay:3s;"></div>
            <div class="det-box" style="top:45%; left:45%; width:40px; height:40px;
                                          animation-delay:5s;"></div>
        </div>

        <!-- Layer 3: Scanning Line -->
        <div style="position:absolute; top:0; left:0; width:100%; height:100%;
                    pointer-events:none; z-index:3;">
            <style>
                .scan-line {
                    position: absolute;
                    left: 0; width: 100%; height: 1px;
                    background: linear-gradient(90deg, transparent, #00d4aa, transparent);
                    box-shadow: 0 0 12px rgba(0,212,170,0.25);
                    animation: scan-down 8s ease-in-out infinite;
                }
                @keyframes scan-down {
                    0%   { top: 0; opacity: 0; }
                    10%  { opacity: 1; }
                    90%  { opacity: 1; }
                    100% { top: 100%; opacity: 0; }
                }
            </style>
            <div class="scan-line"></div>
        </div>

    </div>
    """,
    height=500,
)

# ---------------------------------------------------------------------------
# 2. STATISTICS ROW (animated JS counters)
# ---------------------------------------------------------------------------
tracker = st.session_state.tracker
summary = tracker.summary()

# Images Processed
images_processed = summary.get("count", 0)

# Detections Performed (sum of all historical detection counts)
try:
    detect_counts = getattr(tracker, "_detect_counts", deque())
    total_detections = sum(detect_counts)
except Exception:
    total_detections = 0

# Models Available
models_available = len(scan_models())

# System Health (cache CPU call for the session to avoid repeated 0.5s waits)
if "_cpu_health" not in st.session_state:
    try:
        st.session_state._cpu_health = max(0, min(100, round(100 - cpu_percent())))
    except Exception:
        st.session_state._cpu_health = 100
system_health = st.session_state._cpu_health

st.markdown("<div style='margin:30px 0 10px;'></div>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    components.html(_js_counter("Images Processed", images_processed, uid="c1"), height=120)
with c2:
    components.html(_js_counter("Detections Performed", total_detections, uid="c2"), height=120)
with c3:
    components.html(_js_counter("Models Available", models_available, uid="c3"), height=120)
with c4:
    components.html(
        _js_counter("System Health", system_health, suffix="operational", uid="c4"),
        height=120,
    )

# ---------------------------------------------------------------------------
# 3. CROSS-PLATFORM READINESS
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:40px 0 10px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='text-align:center; color:#e2e8f0; font-size:1.4rem; font-weight:600; margin-bottom:8px;'>"
    "Deployment Ready</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#94a3b8; font-size:0.85rem; margin-bottom:24px;'>"
    "Built for modern infrastructure — deploy anywhere, scale everywhere."
    "</p>",
    unsafe_allow_html=True,
)

readiness = [
    ("🌐", "Web Platform"),
    ("📱", "iOS Compatible"),
    ("🤖", "Android Compatible"),
    ("☁️", "Cloud Ready"),
    ("🐳", "Docker Ready"),
]
r_cols = st.columns(5)
for idx, (icon, label) in enumerate(readiness):
    with r_cols[idx]:
        st.markdown(
            f"""
            <div style="text-align:center; padding:18px 8px;
                        background:rgba(20,25,40,0.4); border:1px solid rgba(255,255,255,0.05);
                        border-radius:14px;">
                <div style="font-size:1.6rem; margin-bottom:6px;">{icon}</div>
                <div style="color:#e2e8f0; font-size:0.8rem; font-weight:500;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# 4. PLATFORM SHOWCASE
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:40px 0 10px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='text-align:center; color:#e2e8f0; font-size:1.4rem; font-weight:600; margin-bottom:8px;'>"
    "Supported Platforms</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#94a3b8; font-size:0.85rem; margin-bottom:24px;'>"
    "Seamless integration across every layer of your stack."
    "</p>",
    unsafe_allow_html=True,
)

showcase = [
    ("🌐", "Web", "Browser-based inference"),
    ("📱", "iOS", "Native mobile support"),
    ("🤖", "Android", "Edge deployment ready"),
    ("🐳", "Docker", "Containerized for scale"),
    ("☁️", "Cloud", "AWS / GCP / Azure"),
]
s_cols = st.columns(5)
for idx, (icon, name, tag) in enumerate(showcase):
    with s_cols[idx]:
        st.markdown(
            f"""
            <div style="text-align:center; padding:22px 10px;
                        background:rgba(20,25,40,0.4); border:1px solid rgba(255,255,255,0.05);
                        border-radius:14px;">
                <div style="font-size:1.6rem; margin-bottom:6px;">{icon}</div>
                <div style="color:#e2e8f0; font-size:0.85rem; font-weight:600; margin-bottom:4px;">{name}</div>
                <div style="color:#64748b; font-size:0.75rem;">{tag}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# 5. FEATURE GRID
# ---------------------------------------------------------------------------
st.markdown("<div style='margin:40px 0 10px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='text-align:center; color:#e2e8f0; font-size:1.5rem; font-weight:600; margin-bottom:30px;'>"
    "Platform Capabilities</h2>",
    unsafe_allow_html=True,
)

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
# 6. FOOTER
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
