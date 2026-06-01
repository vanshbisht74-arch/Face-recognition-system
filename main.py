# ============================================================
# main.py  — Entry point
# ============================================================

import sys
import os
import tkinter as tk
from gui import MainDashboard

REQUIRED_DIRS = ["known_faces", "attendance", "database", "assets"]


def check_python_version():
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 7):
        print(f"ERROR: Python 3.7+ required. You have {major}.{minor}")
        sys.exit(1)
    print(f"✅ Python {major}.{minor} — OK")


def create_required_directories():
    for d in REQUIRED_DIRS:
        os.makedirs(d, exist_ok=True)
    print("✅ Project folders verified.")


def check_dependencies():
    required = {
        "cv2"      : "opencv-python",
        "deepface" : "deepface",
        "PIL"      : "Pillow",
        "pandas"   : "pandas",
        "numpy"    : "numpy",
    }
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print("ERROR: Missing libraries:")
        for pkg in missing:
            print(f"   pip install {pkg}")
        sys.exit(1)
    print("✅ All dependencies found — OK")


def main():
    print("=" * 50)
    print("  Face Recognition Attendance System")
    print("=" * 50)

    check_python_version()
    check_dependencies()
    create_required_directories()

    print("✅ All checks passed. Launching GUI...")

    root = tk.Tk()
    root.configure(bg="#1a1a2e")   # Set dark bg immediately — prevents white flash
    root.withdraw()                # Hide window until fully loaded

    icon_path = os.path.join("assets", "icon.png")
    if os.path.exists(icon_path):
        try:
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)
        except Exception:
            pass

    app = MainDashboard(root)
    root.deiconify()               # Now show the fully-built window
    root.mainloop()
    print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()