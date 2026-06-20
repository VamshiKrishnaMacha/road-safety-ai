"""Glassmorphism card helpers for premium UI elements."""
import streamlit as st


def metric_card(label: str, value: str, delta: str = "", positive: bool = True) -> None:
    """Custom metric with gradient text, inside a glass card."""
    delta_html = ""
    if delta:
        delta_color = "#10b981" if positive else "#ef4444"
        delta_html = f"<div style='color:{delta_color}; font-size:0.9rem; margin-top:8px;'>{delta}</div>"
    
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="color:#94a3b8; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:12px;">{label}</div>
        <div style="font-size:2.8rem; font-weight:700; background:linear-gradient(90deg,#00d4aa,#7c3aed); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def info_card(title: str, items: list[dict]) -> None:
    """Info card with key-value pairs. items = [{"label":"...","value":"..."}]"""
    items_html = ""
    for item in items:
        items_html += f"""
        <div class="info-item">
            <span class="info-label">{item['label']}</span>
            <span class="info-value">{item['value']}</span>
        </div>
        """
    
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color:#e2e8f0; font-size:1.1rem; font-weight:600; margin-bottom:16px; border-bottom:1px solid rgba(255,255,255,0.06); padding-bottom:12px;">{title}</h3>
        <div>{items_html}</div>
    </div>
    """, unsafe_allow_html=True)


def status_card(title: str, status: str, status_color: str, description: str = "") -> None:
    """Card with a colored status badge and description."""
    badge_class = "status-active" if status.lower() == "active" else "status-inactive"
    if status_color in ["#00d4aa", "green", "teal"]:
        badge_class = "status-active"
    elif status_color in ["#f59e0b", "orange", "yellow"]:
        badge_class = "status-warning"
    elif status_color in ["#ef4444", "red"]:
        badge_class = "status-error"
    
    desc_html = f"<p style='color:#94a3b8; font-size:0.9rem; margin-top:12px;'>{description}</p>" if description else ""
    
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color:#e2e8f0; font-size:1rem; font-weight:600; margin-bottom:10px;">{title}</h3>
        <span class="status-badge {badge_class}">{status}</span>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def feature_card(icon: str, title: str, description: str) -> None:
    """Descriptive feature card for landing page."""
    st.markdown(f"""
    <div class="feature-card">
        <span class="feature-icon">{icon}</span>
        <h3 class="feature-title">{title}</h3>
        <p class="feature-description">{description}</p>
    </div>
    """, unsafe_allow_html=True)


def tech_card(name: str, icon: str = "") -> None:
    """Technology stack card for About page."""
    st.markdown(f"""
    <div class="tech-card">
        <div style="font-size:2.5rem;">{icon}</div>
        <div class="tech-name">{name}</div>
    </div>
    """, unsafe_allow_html=True)