"""Application constants: colors, paths, defaults."""
import os

# Colors
COLORS = {
    "bg": "#0a0e17",
    "bg_secondary": "#0f1629",
    "card_bg": "rgba(20, 25, 40, 0.6)",
    "card_bg_solid": "#141928",
    "text": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "accent": "#00d4aa",
    "accent_secondary": "#7c3aed",
    "accent_glow": "rgba(0, 212, 170, 0.25)",
    "border": "rgba(255, 255, 255, 0.08)",
    "border_accent": "rgba(0, 212, 170, 0.3)",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
}

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
CSS_PATH = os.path.join(ASSETS_DIR, "css", "theme.css")
JS_PATH = os.path.join(ASSETS_DIR, "js", "particles.html")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
FAILED_CASES_DIR = os.path.join(PROJECT_ROOT, "failed_cases")
PAGES_DIR = os.path.join(PROJECT_ROOT, "pages")

# Model files (must be preserved)
MODEL_FILES = [
    "yolov8.pt",
    "yolov11.pt",
    "yolov8_RDD_cracks.pt",
]

# Defaults
DEFAULTS = {
    "conf": 0.25,
    "iou": 0.45,
    "max_history": 500,
    "refresh_interval": 3,
}