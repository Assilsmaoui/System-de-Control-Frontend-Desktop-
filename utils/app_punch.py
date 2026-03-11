import os
import sys
from datetime import datetime
import requests
import getpass

# Pour capture écran (optionnel)
import mss
import mss.tools
import platform

USERNAME = os.environ.get("APP_LOGGED_USER") or getpass.getuser()
APP_NAME = "Application Système de Contrôle (Qt)"

# Pour la capture écran
screenshot_dir = "screenshotsaa"
os.makedirs(screenshot_dir, exist_ok=True)

def take_screenshot(event):
    filename = f"{screenshot_dir}/punch_{event}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            img = sct.grab(monitor)
            mss.tools.to_png(img.rgb, img.size, output=filename)
        return filename
    except Exception:
        return ""

def send_punch(event, start, end=None):
    data = {
        "user": USERNAME,
        "app": APP_NAME,
        "start_app": start.strftime('%Y-%m-%d %H:%M:%S'),
        "fin_app": end.strftime('%Y-%m-%d %H:%M:%S') if end else None,
        "duree": round((end - start).total_seconds(), 2) if end else None,
        "event": event
    }
    try:
        requests.post("http://localhost:8000/app_punch/", json=data)
    except Exception:
        pass

# --- Pointage démarrage ---
START_TIME = datetime.now()
take_screenshot("start")
send_punch("start", START_TIME)

# --- Attendre la fermeture de l'app principale ---
try:
    input("Appuyez sur Entrée pour simuler la fermeture de l'application...")
except KeyboardInterrupt:
    pass

END_TIME = datetime.now()
take_screenshot("fin")
send_punch("fin", START_TIME, END_TIME)
