import sys
import importlib
import subprocess

packages = {
    "mlflow": "MLflow",
    "shap": "SHAP",
    "sklearn": "scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "matplotlib": "Matplotlib"
    "streamlit": "Streamlit"
}

def check_package(name, label):
    try:
        pkg = importlib.import_module(name)
        print(f"\033[92m✅ {label} version: {pkg.__version__}\033[0m")
        return True
    except ImportError:
        print(f"\033[91m❌ {label} is NOT installed!\033[0m")
        return False

def install_package(name):
    print(f"\033[93m⬇️  Installing '{name}' via pip...\033[0m")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", name])
        print(f"\033[92m✅ '{name}' installed successfully.\033[0m\n")
    except subprocess.CalledProcessError:
        print(f"\033[91m❌ Failed to install '{name}'. Please install it manually.\033[0m\n")

print("🔎 Environment:", sys.executable)
missing = []

# Check and collect missing packages
for pkg_name, display_name in packages.items():
    if not check_package(pkg_name, display_name):
        missing.append(pkg_name)

# Ask and install missing packages
if missing:
    print("\n🧩 The following packages are missing:")
    for m in missing:
        print(f"   - {m}")
    response = input("\n❓ Do you want to install all missing packages now? [y/N]: ").strip().lower()
    if response == "y":
        for m in missing:
            install_package(m)
    else:
        print("\n⚠️ Skipped installation. Please install manually if needed.")
else:
    print("\n🎉 All required packages are installed.")
