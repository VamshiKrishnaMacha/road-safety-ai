"""Minimal MLflow demonstration for Road Safety AI."""
import os

os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

import mlflow

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MLFLOW_TRACKING_URI = os.path.join(PROJECT_ROOT, "mlruns")
EXPERIMENT_NAME = "road_safety_ai"

MODELS = [
    {
        "file": "yolov8.pt",
        "model_name": "YOLOv8",
        "project_name": "Road Safety Intelligence Platform",
        "deployment_type": "Streamlit + Docker",
    },
    {
        "file": "yolov11.pt",
        "model_name": "YOLOv11",
        "project_name": "Road Safety Intelligence Platform",
        "deployment_type": "Streamlit + Docker",
    },
    {
        "file": "yolov8_RDD_cracks.pt",
        "model_name": "YOLOv8 RDD Cracks",
        "project_name": "Road Safety Intelligence Platform",
        "deployment_type": "Streamlit + Docker",
    },
]


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"Experiment: {EXPERIMENT_NAME}")
    print("-" * 50)

    for info in MODELS:
        model_file = info["file"]
        model_path = os.path.join(PROJECT_ROOT, model_file)

        if not os.path.exists(model_path):
            print(f"WARNING: Model file not found – {model_path}")
            continue

        with mlflow.start_run(run_name=model_file):
            # Log parameters
            mlflow.log_param("model_name", info["model_name"])
            mlflow.log_param("project_name", info["project_name"])
            mlflow.log_param("deployment_type", info["deployment_type"])
            mlflow.log_param("model_file", model_file)
            mlflow.log_param(
                "model_size_mb",
                round(os.path.getsize(model_path) / (1024 * 1024), 2),
            )

            # Log model artifact
            mlflow.log_artifact(model_path)

            print(f"  Logged run: {model_file}")
            print(f"    model_name      : {info['model_name']}")
            print(f"    project_name    : {info['project_name']}")
            print(f"    deployment_type : {info['deployment_type']}")

    print("-" * 50)
    print("Done. Start MLflow UI with:")
    print("  mlflow ui --backend-store-uri ./mlruns --port 5000")


if __name__ == "__main__":
    main()
