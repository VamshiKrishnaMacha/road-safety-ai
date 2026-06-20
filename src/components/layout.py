"""Layout components: CSS injection, page wrappers, sidebar."""
import streamlit as st
import os


def inject_custom_css(css_path: str = "assets/css/theme.css") -> None:
    """Inject theme.css into the page. Call at the VERY TOP of every page."""
    
    if not os.path.exists(css_path):
        st.warning(f"Theme CSS not found: {css_path}")
        return

    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )

    except UnicodeDecodeError:
        st.error(
            f"Could not read CSS file '{css_path}'. "
            "The file is not valid UTF-8. "
            "Please reopen and save theme.css as UTF-8."
        )

    except Exception as e:
        st.error(f"Error loading CSS: {e}")


def page_header(title: str, subtitle: str = "") -> None:
    """Render a premium page header with gradient underline."""
    st.markdown(f"""
    <div class="page-header">
        <h2>{title}</h2>
        {f'<p class="page-header-subtitle">{subtitle}</p>' if subtitle else ''}
        <div class="page-header-underline"></div>
    </div>
    """, unsafe_allow_html=True)


def hero_section(main_title: str, subtitle: str) -> None:
    """Full-width hero with animated gradient text. Used only on Landing."""
    st.markdown(f"""
    <div class="hero-section">
        <h1 class="hero-title">{main_title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def glass_container():
    """Return a markdown string that creates a glass card wrapper."""
    return st.markdown("<div class='glass-card'>", unsafe_allow_html=True)


def close_glass_container():
    """Close the glass card div."""
    st.markdown("</div>", unsafe_allow_html=True)