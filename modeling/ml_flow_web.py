#!/usr/bin/env python
import subprocess
import sys


def start_mlflow_ui(host='127.0.0.1', port=5000):
    """
    Start the MLflow UI by invoking the 'mlflow ui' command.

    The MLflow UI provides an HTTP endpoint (default http://127.0.0.1:5000)
    where you can view and manage your experiments, runs, parameters, metrics,
    and model artifacts.
    """
    command = ["mlflow", "ui", "--host", host, "--port", str(port)]
    try:
        print(f"Starting MLflow UI on http://{host}:{port}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as err:
        print("Error starting MLflow UI:", err)
        sys.exit(1)


if __name__ == '__main__':
    start_mlflow_ui()
