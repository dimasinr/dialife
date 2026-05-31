"""
WSGI config for dialife project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

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


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dialife.settings')

application = get_wsgi_application()
