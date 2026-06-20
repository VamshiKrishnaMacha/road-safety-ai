"""05_Model_Center.py — Model Center: auto-discover and manage .pt model files."""
import os
import sys
from datetime import datetime

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.components.layout import inject_custom_css, page_header
from src.components.cards import metric_card


def get_models() -> list[dict]:
    """Auto-discover .pt files in the project root directory."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models = []
    for f in sorted(os.listdir(root)):
        if f.endswith(".pt"):
            path = os.path.join(root, f)
            try:
                size_mb = os.path.getsize(path) / (1024 * 1024)
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
            except Exception:
                size_mb = 0.0
                mtime = "Unknown"
            models.append({"name": f, "size_mb": size_mb, "mtime": mtime, "path": path})
    return models


# ── Page setup ────────────────────────────────────────────────────────────────
inject_custom_css()
page_header("Model Center", "AI Model Management")

# ── Session state: active model ───────────────────────────────────────────────
models = get_models()
model_names = [m["name"] for m in models]

if "active_model" not in st.session_state:
    st.session_state.active_model = model_names[0] if model_names else None

# Validate that stored active_model still exists; reset if not
if st.session_state.active_model not in model_names:
    st.session_state.active_model = model_names[0] if model_names else None

# ── Model Cards ───────────────────────────────────────────────────────────────
st.markdown("#### Available Models")

if not models:
    st.info("No .pt model files found in the project root.")
else:
    for model in models:
        is_active = model["name"] == st.session_state.active_model

        # Apply CSS class: active gets both model-card and active modifier
        card_class = "model-card active" if is_active else "model-card"

        # Use Streamlit container + columns — NO raw HTML glass-card nesting
        with st.container():
            left_col, right_col = st.columns([0.7, 0.3])

            with left_col:
                st.markdown(
                    f'<div class="model-name">{model["name"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="model-meta">'
                    f'{model["size_mb"]:.1f} MB &nbsp;|&nbsp; Updated {model["mtime"]}</div>',
                    unsafe_allow_html=True,
                )
                if is_active:
                    st.markdown(
                        '<div class="model-meta" style="color:#00d4aa;">Currently Active</div>',
                        unsafe_allow_html=True,
                    )

            with right_col:
                if is_active:
                    st.markdown(
                        '<div style="text-align:center; padding-top:4px;">'
                        '<span style="background:rgba(0,212,170,0.2);color:#00d4aa;'
                        'padding:4px 14px;border-radius:20px;font-size:0.78rem;'
                        'font-weight:600;letter-spacing:0.05em;">ACTIVE</span>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<div style="text-align:center; padding-top:4px;">'
                        '<span style="background:rgba(124,58,237,0.2);color:#a78bfa;'
                        'padding:4px 14px;border-radius:20px;font-size:0.78rem;'
                        'font-weight:600;letter-spacing:0.05em;">READY</span>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                    if st.button("Load Model", key=f"load_{model['name']}"):
                        st.session_state.active_model = model["name"]
                        st.rerun()

        st.markdown(f"<div class='{card_class}'></div>", unsafe_allow_html=True)
        st.divider()

# ── Summary Row ───────────────────────────────────────────────────────────────
st.markdown("#### Model Summary")

total_size = sum(m["size_mb"] for m in models)
active_name = st.session_state.active_model or "—"

col1, col2, col3 = st.columns(3)

with col1:
    metric_card("Active Model", active_name)

with col2:
    metric_card("Available Models", str(len(models)))

with col3:
    metric_card("Total Size", f"{total_size:.1f} MB")