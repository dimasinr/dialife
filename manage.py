#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Auto-fix for OpenCV GUI dependencies on headless servers
try:
    import cv2
except ImportError as e:
    if "libxcb" in str(e) or "libGL" in str(e):
        import subprocess
        print("Detected headless environment: Reinstalling opencv-python-headless...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "opencv-python", "opencv-python-headless"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python-headless"])
        except Exception as err:
            print(f"Failed to auto-reinstall opencv-python-headless: {err}")



def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dialife.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
