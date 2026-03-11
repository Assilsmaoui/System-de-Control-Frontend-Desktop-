import os
from datetime import datetime
import requests
from views.main_window import run_app_qt

def take_screenshot(label):
    try:
        import mss, mss.tools
        screenshot_dir = "screenshotsaa"
        os.makedirs(screenshot_dir, exist_ok=True)
        filename = f"{screenshot_dir}/punch_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            img = sct.grab(monitor)
            mss.tools.to_png(img.rgb, img.size, output=filename)
        return filename
    except Exception:
        return ""



def send_pointage(start, end=None):
    app = "Application Système de Contrôle (Qt)"
    # Lire le nom d'utilisateur authentifié depuis la variable d'environnement
    user = os.environ.get("APP_LOGGED_USER", "")
    data = {
        "user": user,
        "app": app,
        "start_app": start.strftime('%Y-%m-%d %H:%M:%S'),
        "fin_app": end.strftime('%Y-%m-%d %H:%M:%S') if end else None,
        "duree": round((end - start).total_seconds(), 2) if end else None
    }
    try:
        requests.post("http://localhost:8000/pointage", json=data)
    except Exception:
        pass

if __name__ == "__main__":
    START_TIME = datetime.now()
    take_screenshot("start")
    # Le pointage de démarrage sera envoyé après authentification
    try:
        run_app_qt()
    finally:
        END_TIME = datetime.now()
        take_screenshot("fin")
        send_pointage(START_TIME, END_TIME)
