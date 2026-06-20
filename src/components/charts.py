"""Plotly-based chart helpers with dark theme."""
import plotly.graph_objects as go
import pandas as pd
import streamlit as st


# Dark theme defaults
DARK_PAPER_BG = "#0a0e17"
DARK_PLOT_BG = "#0f1629"
DARK_FONT_COLOR = "#e2e8f0"
DARK_GRID_COLOR = "rgba(255, 255, 255, 0.06)"
ACCENT_COLOR = "#00d4aa"
ACCENT_SECONDARY = "#7c3aed"


def _get_dark_layout(title: str = "") -> dict:
    """Return common dark theme layout parameters."""
    return dict(
        paper_bgcolor=DARK_PAPER_BG,
        plot_bgcolor=DARK_PLOT_BG,
        font=dict(color=DARK_FONT_COLOR, size=12),
        title=dict(text=title, font=dict(color=DARK_FONT_COLOR, size=16)),
        margin=dict(l=40, r=40, t=60, b=40),
    )


def gauge_chart(value: float, title: str, max_val: float = 100, threshold: float = 70) -> None:
    """Plotly gauge indicator with dark theme."""
    # Determine color based on threshold
    if value >= threshold:
        color = ACCENT_COLOR
    else:
        color = ACCENT_SECONDARY
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": DARK_FONT_COLOR},
            "bar": {"color": color, "thickness": 0.3},
            "bg": DARK_PAPER_BG,
            "borderwidth": 0,
            "steps": [
                {"range": [0, threshold * 0.6], "color": "rgba(0, 212, 170, 0.1)"},
                {"range": [threshold * 0.6, threshold], "color": "rgba(0, 212, 170, 0.2)"},
                {"range": [threshold, max_val], "color": "rgba(239, 68, 68, 0.2)"},
            ],
        },
        number={
            "suffix": "%" if max_val == 100 else "",
            "font": {"color": color, "size": 32},
        },
        title={"text": title, "font": {"color": DARK_FONT_COLOR, "size": 14}},
    ))
    
    fig.update_layout(
        **_get_dark_layout(),
        height=200,
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(data_df: pd.DataFrame, x: str, y: str, title: str = "") -> None:
    """Plotly dark-themed bar chart."""
    fig = go.Figure(go.Bar(
        x=data_df[x],
        y=data_df[y],
        marker=dict(
            color=data_df[y],
            colorscale=[[0, "rgba(0, 212, 170, 0.4)"], [1, ACCENT_COLOR]],
            line=dict(color=ACCENT_COLOR, width=1),
        ),
        text=data_df[y],
        textposition="outside",
        textfont=dict(color=DARK_FONT_COLOR),
    ))
    
    fig.update_layout(
        **_get_dark_layout(title),
        xaxis=dict(
            title=x,
            showgrid=True,
            gridcolor=DARK_GRID_COLOR,
            tickfont=dict(color=DARK_FONT_COLOR),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=DARK_GRID_COLOR,
            tickfont=dict(color=DARK_FONT_COLOR),
        ),
        height=300,
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def line_chart(data_df: pd.DataFrame, x: str, y: str, title: str = "") -> None:
    """Plotly dark-themed line chart."""
    fig = go.Figure(go.Scatter(
        x=data_df[x],
        y=data_df[y],
        mode="lines+markers",
        line=dict(color=ACCENT_COLOR, width=2),
        marker=dict(color=ACCENT_COLOR, size=6, symbol="circle"),
        fill="tozeroy",
        fillcolor="rgba(0, 212, 170, 0.1)",
    ))
    
    fig.update_layout(
        **_get_dark_layout(title),
        xaxis=dict(
            showgrid=True,
            gridcolor=DARK_GRID_COLOR,
            tickfont=dict(color=DARK_FONT_COLOR),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=DARK_GRID_COLOR,
            tickfont=dict(color=DARK_FONT_COLOR),
        ),
        height=300,
        showlegend=False,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def heatmap(z: list, x_labels: list, y_labels: list, title: str = "") -> None:
    """Plotly dark-themed heatmap."""
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0, DARK_PLOT_BG],
            [0.5, "rgba(0, 212, 170, 0.4)"],
            [1, ACCENT_COLOR],
        ],
        showscale=True,
        colorbar=dict(
            tickfont=dict(color=DARK_FONT_COLOR),
            title=dict(font=dict(color=DARK_FONT_COLOR)),
        ),
    ))
    
    fig.update_layout(
        **_get_dark_layout(title),
        height=350,
        xaxis=dict(tickfont=dict(color=DARK_FONT_COLOR)),
        yaxis=dict(tickfont=dict(color=DARK_FONT_COLOR)),
    )
    
    st.plotly_chart(fig, use_container_width=True)